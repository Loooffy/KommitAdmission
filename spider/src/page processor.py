import os
import requests
from markitdown import MarkItDown
from urllib.parse import urlparse
from datetime import datetime
import concurrent.futures
import threading
from pymongo import MongoClient
import hashlib
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from document_store import DocumentStore

# Add a thread-safe print function
print_lock = threading.Lock()
def safe_print(message):
    with print_lock:
        print(message)

document_store = DocumentStore()

load_dotenv()
PAGE_PROCESSOR_URL = os.getenv('PAGE_PROCESSOR_URL', 'http://html-to-markdown:3000/convert')

def convert_html_to_markdown(url):
    try:
        response = requests.post(
            PAGE_PROCESSOR_URL,
            json={'url': url}
        )
        response.raise_for_status()
        return response.json()['markdown']
    except requests.RequestException as e:
        raise Exception(f"Failed to convert using local service: {str(e)}")

class DocumentProcessor(ABC):
    @abstractmethod
    def process(self, link: str, output_dir: str) -> dict:
        pass

class MarkdownConverter:
    def convert_markdown(self, input_file_name):
        md = MarkItDown()
        result = md.convert(input_file_name)
        return result

class PDFProcessor(DocumentProcessor):
    def process(self, link: str, output_dir: str) -> dict:
        response = requests.get(link, stream=True)
        response.raise_for_status()
        
        temp_pdf_path = os.path.join(output_dir, f"temp_{threading.get_ident()}.pdf")
        
        with open(temp_pdf_path, 'wb') as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    pdf_file.write(chunk)
        
        converter = MarkdownConverter()
        markdown_content = converter.convert_markdown(temp_pdf_path)
        
        os.remove(temp_pdf_path)
        
        return {
            'content': markdown_content.text_content,
            'type': 'pdf'
        }

class HTMLProcessor(DocumentProcessor):
    def process(self, link: str, output_dir: str) -> dict:
        markdown_content = convert_html_to_markdown(link)
        return {
            'content': markdown_content,
            'type': 'html'
        }

class DocumentProcessorFactory:
    @staticmethod
    def create_processor(link: str) -> DocumentProcessor:
        if link.lower().endswith('.pdf'):
            return PDFProcessor()
        return HTMLProcessor()

def process_single_link(link, output_dir):
    try:
        processor = DocumentProcessorFactory.create_processor(link)
        result = processor.process(link, output_dir)
        
        success = document_store.store_document(
            url=link,
            content=result['content'],
            doc_type=result['type']
        )
        
        return success
    except Exception as e:
        safe_print(f"Failed to process {link}: {e}")
        return False

def process_links(school_name, max_workers=5):
    links_collection = db['school_links']
    links = [doc['url'] for doc in links_collection.find({'school': school_name})]

    output_dir = os.path.join(f'../data/{school_name}', f'{school_name}_temp')
    os.makedirs(output_dir, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_link = {
            executor.submit(process_single_link, link, output_dir): link 
            for link in links
        }

        completed = 0
        total = len(links)
        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            completed += 1
            safe_print(f"Progress: {completed}/{total} links processed")

    os.rmdir(output_dir)

def merge_markdown_files(school_name):
    """Merge all markdown documents with school metadata"""
    return document_store.store_school_documents(school_name)