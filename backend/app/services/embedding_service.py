from typing import List
from openai import OpenAI
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    def generate_embedding(self, text: str) -> List[float]:
        """Generate a 1536-dimensional embedding using OpenAI."""
        if not text:
            return [0.0] * 1536
            
        response = self.client.embeddings.create(
            input=[text.replace("\n", " ")],
            model=self.model
        )
        return response.data[0].embedding

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate batch embeddings using OpenAI, processing in chunks of 100."""
        if not texts:
            return []
            
        all_embeddings = []
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Clean texts (OpenAI recommendation)
            batch = [t.replace("\n", " ") for t in batch]
            
            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )
            all_embeddings.extend([item.embedding for item in response.data])
            
        return all_embeddings

# Singleton instance
embedding_service = EmbeddingService()
