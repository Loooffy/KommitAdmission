import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urljoin, urldefrag
import requests
import json
import os
from datetime import datetime
import concurrent.futures
import threading
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import time
import urllib3
from mongodb_manager import MongoDBManager
from utils.helper import get_school_abbreviation

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Thread-safe print function
print_lock = threading.Lock()
def safe_print(message):
    with print_lock:
        print(message)

class WebScraper:
    def __init__(self, url):
        self.url = url
        parsed_url = urlparse(url)
        self.domain = parsed_url.netloc
        if self.domain.startswith('www.'):
            self.domain = self.domain[4:]
        self.school_name = get_school_abbreviation(url)
        self.links = set()
        self.links_lock = threading.Lock()
        self.queue = Queue()
        self.visited = set()
        self.max_workers = 8
        self.last_save_count = 0
        self.save_threshold = 100
        self.results_dir = "crawl_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Initialize MongoDB connection
        self.mongodb = MongoDBManager()
        try:
            self.mongodb.connect()
            safe_print("Successfully connected to MongoDB")
        except Exception as e:
            safe_print(f"Error connecting to MongoDB: {str(e)}")
            raise
            
        safe_print(f"[DEBUG] WebScraper initialized with URL: {url}, domain: {self.domain}")

    def save_results(self):
        try:
            self.mongodb.save_crawl_results(
                url=self.url,
                school_name=self.school_name,
                links=self.links
            )
            safe_print(f"Saved {len(self.links)} links to MongoDB")
        except Exception as e:
            safe_print(f"Error saving to MongoDB: {str(e)}")

    def process_url(self, url):
        base_url, _ = urldefrag(url)
        
        if base_url in self.visited:
            safe_print(f"DEBUG: Skipping already visited URL: {base_url}")
            return
        
        try:
            safe_print(f"DEBUG: Starting to process URL: {base_url}")
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                timeout=(5, 10),
                verify=False
            )
            self.visited.add(base_url)
            
            safe_print(f"DEBUG: Response status code: {response.status_code} for {base_url}")
            
            if response.status_code == 200:
                selector = scrapy.Selector(text=response.text)
                found_links = []
                all_links = selector.css("a::attr(href)").getall()
                safe_print(f"DEBUG: Found {len(all_links)} raw links on page {base_url}")
                
                for link in all_links:
                    full_url = urljoin(url, link)

                    base_full_url, _ = urldefrag(full_url)
                    parsed_url = urlparse(base_full_url)
                    initial_parsed = urlparse(self.url)
                    
                    if (parsed_url.netloc.replace('www.', '') == self.domain and 
                        parsed_url.path.startswith(initial_parsed.path) and
                        base_full_url not in self.visited):
                        found_links.append(base_full_url)
                
                safe_print(f"DEBUG: Found {len(found_links)} valid links on page {base_url}")
                
                with self.links_lock:
                    for base_full_url in found_links:
                        self.links.add(base_full_url)
                        self.queue.put(base_full_url)
                        safe_print(f"DEBUG: Added to queue: {base_full_url}")
                    
                    if len(self.links) - self.last_save_count >= self.save_threshold:
                        safe_print(f"DEBUG: Saving results - total links: {len(self.links)}")
                        self.save_results()
                        self.last_save_count = len(self.links)
                        
        except requests.exceptions.Timeout:
            safe_print(f"DEBUG: Timeout while processing {url} (timeout=(5, 10))")
        except requests.exceptions.SSLError:
            safe_print(f"DEBUG: SSL Error while processing {url}")
        except requests.exceptions.ConnectionError:
            safe_print(f"DEBUG: Connection Error while processing {url}")
        except Exception as e:
            safe_print(f"DEBUG: Unexpected error processing {url}: {str(e)}")
            safe_print(f"DEBUG: Error type: {type(e).__name__}")
        finally:
            safe_print(f"DEBUG: Marking as visited: {base_url}")
            self.visited.add(base_url)

    def scrape(self):
        try:
            self.queue.put(self.url)
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                while True:
                    try:
                        current_urls = []
                        while not self.queue.empty():
                            url = self.queue.get()
                            if url not in self.visited:
                                current_urls.append(url)
                        
                        if not current_urls:
                            break
                        
                        futures = list(executor.map(self.process_url, current_urls))
                        
                    except Exception as e:
                        safe_print(f"Error in scrape process: {str(e)}")
                        break
            
            end_time = time.time()
            safe_print(f"[DEBUG] Crawling finished in {end_time - start_time:.2f} seconds. Found {len(self.links)} links")
            
            self.save_results()
            return sorted(list(self.links))
        finally:
            self.mongodb.close()
            safe_print("MongoDB connection closed")