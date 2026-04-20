import os
import tempfile
from typing import Optional, List
from langchain_community.document_loaders import PyPDFLoader
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
        self.embeddings = OllamaEmbeddings(
            model=os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
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

    def ingest_pdf(self, file_path: str, question_code: str, source_uri: str = ""):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        for doc in documents:
            doc.metadata = {"question_code": question_code, "source_uri": source_uri}
            
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(documents)
        
        if chunks:
            self.db.add_documents(chunks)
            return {"count": len(chunks)}
        return {"count": 0}

    def get_context(self, query: str, question_code: str, k: int = 3) -> str:
        results = self.db.similarity_search(query, k=k, filter={"question_code": question_code})
        return "\n\n".join([doc.page_content for doc in results])

# Initialize singleton
rag_service = RAGService()
