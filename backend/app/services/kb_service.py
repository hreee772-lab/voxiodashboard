from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
from app.services.embedding_service import embedding_service
from typing import List, Dict

class KBService:
    async def search_chunks(self, db: AsyncSession, client_id: str, query: str, limit: int = 5) -> List[Dict]:
        try:
            query_embedding = embedding_service.generate_embedding(query)
            
            search_query = text("""
                SELECT content, metadata, 1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                FROM kb_chunks
                WHERE client_id = :client_id
                AND 1 - (embedding <=> CAST(:query_embedding AS vector)) > 0.1
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :limit
            """)
            
            result = await db.execute(search_query, {
                "client_id": client_id,
                "query_embedding": str(query_embedding),
                "limit": limit
            })
            
            rows = result.fetchall()
            print(f"Vector search found {len(rows)} chunks for client {client_id}")
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            print(f"Vector search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def insert_chunk(self, db: AsyncSession, client_id: str, content: str, metadata: Dict, embedding: List[float]):
        """Insert a new chunk with its embedding into the database."""
        query = text("""
            INSERT INTO kb_chunks (client_id, content, metadata, embedding)
            VALUES (:client_id, :content, :metadata, CAST(:embedding AS vector))
        """)
        
        await db.execute(query, {
            "client_id": client_id,
            "content": content,
            "metadata": json.dumps(metadata),
            "embedding": str(embedding)
        })
        await db.commit()

kb_service = KBService()
