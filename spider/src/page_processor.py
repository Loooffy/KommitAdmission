import requests
import os
import threading
import concurrent.futures
from bs4 import BeautifulSoup
from markitdown import MarkItDown
from Qdrant_manager import DocumentStore
from utils import safe_print
from MongoDB_manager import MongoDBManager

class DocumentProcessor:
    def __init__(self):
        self.document_store = DocumentStore()
        self.mongodb_manager = MongoDBManager()
        self.mongodb_manager.connect()

    def process_html(self, url: str) -> str:
        """Process HTML documents by converting them to markdown"""
        return convert_html_to_markdown(url)

    def process_pdf(self, url: str, output_dir: str) -> str:
        """Process PDF documents by downloading and converting to markdown"""
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        temp_pdf_path = os.path.join(output_dir, f"temp_{threading.get_ident()}.pdf")
        
        try:
            with open(temp_pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            
            converter = MarkItDown()
            markdown_content = converter.convert_markdown(temp_pdf_path)
            return markdown_content.text_content
        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    def process_single_document(self, url: str, output_dir: str) -> bool:
        """Process a single document of any supported type"""
        try:
            if url.lower().endswith('.pdf'):
                content = self.process_pdf(url, output_dir)
                doc_type = 'pdf'
            else:
                content = self.process_html(url)
                doc_type = 'html'

            return self.document_store.store_document(
                url=url,
                content=content,
                doc_type=doc_type
            )
        except Exception as e:
            safe_print(f"Failed to process {url}: {e}")
            return False

    def process_school_documents(self, school_name: str, max_workers: int = 5) -> None:
        """Process all documents for a given school"""
        links_collection = self.mongodb_manager.db['school_links']
        links = [doc['url'] for doc in links_collection.find({'school': school_name})]

        output_dir = os.path.join(f'../data/{school_name}', f'{school_name}_temp')
        os.makedirs(output_dir, exist_ok=True)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {
                    executor.submit(self.process_single_document, link, output_dir): link 
                    for link in links
                }

                completed = 0
                total = len(links)
                for future in concurrent.futures.as_completed(future_to_link):
                    completed += 1
                    safe_print(f"Progress: {completed}/{total} links processed")
        finally:
            if os.path.exists(output_dir):
                os.rmdir(output_dir)

    def merge_school_documents(self, school_name: str) -> bool:
        """Merge all documents with school metadata"""
        return self.document_store.store_school_documents(school_name) 