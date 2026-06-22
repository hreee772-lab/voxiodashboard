import anthropic
import openai
from app.core.config import settings
from typing import List, Dict, Optional

class AIService:
    def __init__(self):
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate_response(self, query: str, context_chunks: List[str], bot_config: Dict) -> str:
        # Prepare context
        context_text = "\n\n".join([f"Context chunk {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        
        system_prompt = bot_config.get("system_prompt") or "You are a helpful AI assistant for Voicera. Provide accurate information based on the knowledge base."
        blacklisted_topics = bot_config.get("blacklisted_topics", "")
        
        if blacklisted_topics:
            system_prompt += f"\n\nIMPORTANT: Do not discuss or provide information about the following topics: {blacklisted_topics}"
            
        full_prompt = f"""
Use the following context extracted from our knowledge base to answer the user's question. 
If the answer is not in the context, politely state that you don't have that information in your knowledge base, but offer to escalate to a human specialist if they need more help.

Context:
{context_text}

User Question: {query}
"""

        try:
            if self.anthropic_client:
                # Use the latest requested model
                model = "claude-sonnet-4-20250514"
                response = await self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ]
                )
                return response.content[0].text
            elif self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                return response.choices[0].message.content
            else:
                return "Error: No AI provider (Anthropic or OpenAI) is configured in the environment."
        except Exception as e:
            print(f"AI Service Error: {str(e)}")
            return f"I'm sorry, I'm having trouble processing your request right now. Please try again later. (Error: {str(e)})"

ai_service = AIService()
