import json
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.kb_service import kb_service
from app.core.config import settings
from openai import AsyncOpenAI

class BotService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_bot_response(
        self, 
        db: AsyncSession, 
        client_id: str, 
        user_message: str, 
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Retrieves top KB chunks and constructs a response using GPT-4o-mini.
        """
        if conversation_history is None:
            conversation_history = []
            
        # 1 & 2. Generate embedding and search kb_chunks
        try:
            chunks = await kb_service.search_chunks(
                db=db,
                client_id=client_id,
                query=user_message,
                limit=10
            )
        except Exception as db_err:
            print(f"KB search failed (DB error): {db_err}")
            raise db_err
        
        # 3. Build the context and instructions
        kb_context = "\n---\n".join([c["content"] for c in chunks])
        
        system_instructions = (
            "You are Voicera, a helpful AI support agent.\n"
            "You have been given context from a knowledge base below.\n"
            "Use this context to answer the user's question as \n"
            "helpfully and specifically as possible.\n\n"
            "Rules:\n"
            "- If the context contains ANY relevant information \n"
            "  related to the question, use it to give a helpful answer\n"
            "- Synthesise information from multiple parts of the \n"
            "  context if needed\n"
            "- Do not say you don't have information if the context \n"
            "  has anything relevant\n"
            "- Only say you cannot help if the context has absolutely \n"
            "  nothing related to the topic\n"
            "- Never make up facts, names, emails, or numbers \n"
            "  that are not in the context\n"
            "- Be conversational, clear and direct\n"
            "- If asked about a product or company, describe it \n"
            "  based on what the context says about it\n\n"
            f"KNOWLEDGE BASE CONTEXT:\n{kb_context if chunks else 'No relevant info found in Knowledge Base.'}"
        )
        
        # 4. Call OpenAI API
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instructions},
                    *conversation_history[-10:],
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            bot_text = response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            bot_text = "I'm sorry, I encountered an error processing your request. Please try again or ask to escalate."

        # 5. Return structured response
        return {
            "response": bot_text,
            "confident": bool(chunks),
            "should_escalate": not bool(chunks),
            "chunks_found": len(chunks)
        }

bot_service = BotService()
