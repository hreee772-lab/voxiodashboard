from fastapi import APIRouter, Request, HTTPException
from supabase import create_client
from app.core.config import settings
import re

router = APIRouter(prefix="/voice-kb", tags=["voice_kb"])

def get_supabase():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def clean(text):
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

@router.post("/search")
async def voice_kb_search(request: Request):
    try:
        body = await request.json()
        client_id = body.get("client_id")
        query = body.get("query", "")
        
        if not client_id or not query:
            return {"result": "I don't have information on that topic."}
        
        supabase = get_supabase()
        
        # Keyword search across chunks
        keywords = query.lower().split()
        stop_words = {'what','is','the','a','an','to','for','of','and','or','in','on','at','have','your','how','does','do','tell','me','about'}
        clean_keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
        
        chunks = []
        if clean_keywords:
            for kw in clean_keywords[:3]:
                res = supabase.table("kb_chunks")\
                    .select("content")\
                    .eq("client_id", client_id)\
                    .ilike("content", f"%{kw}%")\
                    .limit(5).execute()
                if res.data:
                    chunks.extend(res.data)
                    if len(chunks) >= 10:
                        break
        
        if not chunks:
            return {"result": "I don't have specific information about that in my knowledge base."}
        
        context = "\n".join([clean(c["content"]) for c in chunks[:5]])
        
        # Use OpenAI to generate a concise voice-friendly answer
        from openai import OpenAI
        oai = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = oai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant. Answer the question using ONLY the context provided. Keep the answer to 2-3 sentences maximum. This will be spoken aloud so be concise and natural."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            max_tokens=150,
            temperature=0.2
        )
        
        result = response.choices[0].message.content
        return {"result": result}
        
    except Exception as e:
        print(f"Voice KB search error: {e}")
        return {"result": "I'm having trouble finding that information right now."}
