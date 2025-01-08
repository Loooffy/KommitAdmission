from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from datetime import datetime
import hashlib
import threading

class DocumentStore:
    def __init__(self, host="qdrant", port=6333, collection_name="documents"):
        self.client = QdrantClient(host, port=port)
        self.collection_name = collection_name
        self._print_lock = threading.Lock()
        
        # Initialize collection
        self._init_collection()
    
    def _init_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1, distance=Distance.COSINE),
                on_disk_payload=True
            )
        except Exception:
            pass
    
    def _safe_print(self, message):
        """Thread-safe print function"""
        with self._print_lock:
            print(message)
    
    def store_document(self, url: str, content: str, doc_type: str) -> bool:
        """Store a single document in Qdrant"""
        try:
            doc_id = hashlib.md5(url.encode()).hexdigest()
            
            point = PointStruct(
                id=int(doc_id[:16], 16),
                vector=[1.0],  # Placeholder vector
                payload={
                    'url': url,
                    'content': content,
                    'type': doc_type,
                    'timestamp': datetime.now().isoformat(),
                    'content_hash': hashlib.md5(content.encode()).hexdigest()
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            self._safe_print(f"Stored {doc_type.upper()} in Qdrant: {url}")
            return True
            
        except Exception as e:
            self._safe_print(f"Failed to store document {url}: {e}")
            return False
    
    def store_school_documents(self, school_name: str) -> int:
        try:
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                with_payload=True,
                with_vectors=True
            )
            points = scroll_result[0]
            
            timestamp = datetime.now().isoformat()
            new_points = []
            
            for point in points:
                payload = point.payload
                doc_id = hashlib.md5(f"{school_name}_{payload['url']}".encode()).hexdigest()
                
                new_point = PointStruct(
                    id=int(doc_id[:16], 16),
                    vector=[1.0],  # Placeholder vector
                    payload={
                        'school': school_name,
                        'url': payload['url'],
                        'content': payload['content'],
                        'type': 'merged',
                        'timestamp': timestamp,
                        'content_hash': payload['content_hash']
                    }
                )
                new_points.append(new_point)
            
            if new_points:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=new_points
                )
            
            self._safe_print(f"Stored school documents in Qdrant for: {school_name}")
            return len(new_points)
            
        except Exception as e:
            self._safe_print(f"Failed to store school documents: {e}")
            return 0 