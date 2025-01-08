from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time
import os
from datetime import datetime
import logging

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.max_retries = 5
        self.retry_delay = 5
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017/')
        self.db_name = os.getenv('MONGODB_DB', 'crawler_db')
        self.collection_name = os.getenv('MONGODB_COLLECTION', 'crawl_results')
        
        # Setup logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('MongoDBManager')
        
    def connect(self):
        """Establish connection to MongoDB with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Attempting to connect to MongoDB at {self.mongodb_uri} (attempt {attempt + 1}/{self.max_retries})")
                self.client = MongoClient(self.mongodb_uri)
                # Test the connection
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.collection = self.db[self.collection_name]
                self.logger.info("Successfully connected to MongoDB")
                return True
            except ConnectionFailure as e:
                self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error("Max retries reached. Could not connect to MongoDB")
                    raise
    
    def save_crawl_results(self, url, school_name, links):
        """Save crawl results to MongoDB using upsert"""
        try:
            document = {
                'url': url,
                'school_name': school_name,
                'total_links': len(links),
                'timestamp': datetime.now(),
                'links': sorted(list(links))
            }
            self.logger.debug(f"Upserting crawl results for {url}")
            result = self.collection.update_one(
                {'url': url},  # filter/query condition
                {'$set': document},  # update/document
                upsert=True  # create if doesn't exist
            )
            self.logger.info(f"Successfully saved crawl results with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            self.logger.error(f"Error saving crawl results: {str(e)}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed") 