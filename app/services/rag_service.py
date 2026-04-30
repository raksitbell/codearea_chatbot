import os
import hashlib
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from app.services.ollama_service import OllamaService

class RAGService:
    """
    Service to handle Retrieval-Augmented Generation using ChromaDB and Ollama embeddings.
    """
    
    def __init__(self):
        config = OllamaService.get_config()
        # Use embedding_model from config, fallback to env, then default
        emb_model = config.get("embedding_model") or os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        self.embeddings = OllamaEmbeddings(
            model=emb_model,
            base_url=config.get("url", "http://localhost:11434")
        )
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "vector_problems"
        self.db = Chroma(
            client=self.chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )

    def delete_chunks(self, question_code: str):
        if not question_code: return
        try:
            self.db._collection.delete(where={"question_code": question_code})
        except: pass

    def sync_question_from_db(self, question_data: dict) -> dict:
        """
        Synchronizes a question from the database into the vector store.
        Skips ingestion if the content hash hasn't changed.
        """
        question_code = question_data.get("code")
        if not question_code:
            return {"status": "error", "message": "Missing question code"}

        # 1. Construct raw text
        raw_text = f"Title: {question_data.get('title', '')}\n\n"
        raw_text += f"Description: {question_data.get('description', '')}\n\n"
        raw_text += f"Constraints: {question_data.get('constraints', '')}\n\n"
        raw_text += f"Solution/Starter Code: {question_data.get('solution', '')}\n"

        # 2. Compute Hash
        content_hash = hashlib.md5(raw_text.encode('utf-8')).hexdigest()

        # 3. Check existing hash in DB to skip if no changes
        try:
            existing = self.db.get(where={"question_code": question_code})
            if existing and existing.get("metadatas") and len(existing["metadatas"]) > 0:
                old_hash = existing["metadatas"][0].get("content_hash")
                if old_hash == content_hash:
                    return {"status": "skipped", "message": "No changes detected, skipping ingestion", "hash": content_hash}
        except Exception:
            # Collection might be empty or query failed, proceed to ingest
            pass

        # 4. If different or not exists, delete old chunks
        self.delete_chunks(question_code)

        # 5. Split and store
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(raw_text)

        if chunks:
            docs = [
                Document(
                    page_content=chunk, 
                    metadata={"question_code": question_code, "content_hash": content_hash}
                )
                for chunk in chunks
            ]
            self.db.add_documents(docs)
            return {"status": "success", "message": f"Ingested {len(docs)} chunks", "hash": content_hash, "count": len(docs)}
        
        return {"status": "success", "message": "No content to ingest", "count": 0}

    def get_context(self, query: str, question_code: str, k: int = 3) -> str:
        results = self.db.similarity_search(query, k=k, filter={"question_code": question_code})
        return "\n\n".join([doc.page_content for doc in results])

# Initialize singleton
rag_service = RAGService()
