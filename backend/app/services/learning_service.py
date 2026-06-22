import json
from typing import List, Dict
from app.core.config import settings
from openai import AsyncOpenAI
from app.services.embedding_service import embedding_service
from app.services.kb_service import kb_service
from app.core.database import async_session

class LearningService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def auto_learn_from_resolution(self, session_id: str, client_id: str, conversation_history: List[Dict]):
        """
        Summarises a resolved conversation and stores it as a new knowledge base chunk.
        """
        if not conversation_history:
            return

        # 1. Build the prompt for GPT
        prompt = (
            "Summarise this support conversation as a knowledge base entry. Format:\n"
            "Question: [what the user asked]\n"
            "Answer: [how it was resolved]\n"
            "Keep it concise and factual."
        )

        # 2. Call GPT-4o-mini
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    *conversation_history
                ],
                max_tokens=500,
                temperature=0.1
            )
            summary = response.choices[0].message.content
        except Exception as e:
            print(f"Learning Service GPT Error: {e}")
            return

        # 3. Generate embedding and store in DB
        try:
            embedding = embedding_service.generate_embedding(summary)
            
            async with async_session() as db:
                await kb_service.insert_chunk(
                    db=db,
                    client_id=client_id,
                    content=summary,
                    metadata={
                        "source": "auto_learned",
                        "session_id": session_id
                    },
                    embedding=embedding
                )
            print(f"Auto-learned from session {session_id} successfully.")
        except Exception as e:
            print(f"Learning Service Storage Error: {e}")

learning_service = LearningService()
