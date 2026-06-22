import os
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.middleware import get_current_user, require_admin
from app.services.embedding_service import embedding_service
from app.services.kb_service import kb_service
from app.services.document_processor import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, chunk_text
from supabase import create_client, Client
from app.core.config import settings

router = APIRouter(prefix="/kb", tags=["knowledge-base"])

@router.get("/summary")
async def get_kb_summary(client_id: str, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT content 
            FROM kb_chunks 
            WHERE client_id = :client_id
            LIMIT 10
        """)
        res = await db.execute(query, {"client_id": client_id})
        rows = res.fetchall()
        
        if not rows:
            return {"summary": ""}
            
        def clean_text(text):
            import re
            text = re.sub(r'\n\s*\n', '\n', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
            
        summary_text = "\n---\n".join([clean_text(row[0]) for row in rows])
        return {"summary": summary_text}
    except Exception as e:
        print(f"Error fetching KB summary: {e}")
        return {"summary": ""}

def get_supabase() -> Client:
    # Use service key for storage operations to bypass RLS
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Get client_id from token
    if "user" in current_user:
        client_id = current_user["user"]["client_id"]
    else:
        client_id = current_user.get("client_id")
    
    # Override with form field client_id if provided (dashboard sends real client_id)
    form_client_id = None
    try:
        form_data = await request.form() if hasattr(request, 'form') else None
    except:
        form_data = None
    
    # Use the client_id from the JWT token directly - it should be correct
    client_id_str = str(client_id)
    
    # Validate file type
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        file_type = "pdf"
        extract_func = extract_text_from_pdf
    elif filename.endswith(".docx"):
        file_type = "docx"
        extract_func = extract_text_from_docx
    elif filename.endswith(".txt"):
        file_type = "txt"
        extract_func = extract_text_from_txt
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, DOCX, or TXT.")

    file_bytes = await file.read()
    
    # Extract text
    try:
        text_content = extract_func(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
        
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="Document contains no readable text.")

    # Chunk text
    chunks = chunk_text(text_content)
    if not chunks:
        raise HTTPException(status_code=400, detail="Failed to chunk document text.")

    # Upload to Supabase Storage
    supabase = get_supabase()
    file_ext = filename.split('.')[-1]
    storage_path = f"{client_id_str}/{uuid.uuid4()}.{file_ext}"
    
    try:
        supabase.storage.from_("kb-documents").upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to storage: {str(e)}")

    file_url = supabase.storage.from_("kb-documents").get_public_url(storage_path)

    # Insert into kb_documents
    doc_query = text("""
        INSERT INTO kb_documents (client_id, file_name, file_type, file_url, status, chunk_count)
        VALUES (:client_id, :file_name, :file_type, :file_url, 'processing', :chunk_count)
        RETURNING id
    """)
    doc_res = await db.execute(doc_query, {
        "client_id": client_id,
        "file_name": file.filename,
        "file_type": file_type,
        "file_url": file_url,
        "chunk_count": len(chunks)
    })
    document_id = doc_res.scalar()
    
    # Generate embeddings and store chunks
    try:
        embeddings = embedding_service.generate_batch_embeddings(chunks)
        
        chunk_query = text("""
            INSERT INTO kb_chunks (client_id, document_id, content, embedding, metadata)
            VALUES (:client_id, :document_id, :content, :embedding, :metadata)
        """)
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            await db.execute(chunk_query, {
                "client_id": client_id,
                "document_id": document_id,
                "content": chunk,
                "embedding": str(embedding), # pgvector string representation
                "metadata": json.dumps({"chunk_index": i})
            })
            
        # Update document status to ready
        update_query = text("UPDATE kb_documents SET status = 'ready' WHERE id = :id")
        await db.execute(update_query, {"id": document_id})
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        # Mark as failed
        fail_query = text("UPDATE kb_documents SET status = 'failed' WHERE id = :id")
        await db.execute(fail_query, {"id": document_id})
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process embeddings: {str(e)}")

    return {"message": "success", "document_id": str(document_id), "chunk_count": len(chunks)}


@router.get("/documents")
async def get_documents(
    client_id_override: str = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if "user" in current_user:
        client_id = current_user["user"]["client_id"]
    else:
        client_id = current_user.get("client_id")
    
    # Allow override with real client_id
    if client_id_override and client_id_override != "70d0188f-ef36-4c79-b0b6-b215e767d859":
        client_id = client_id_override

    client_id_str = str(client_id)
    query = text("""
        SELECT id, file_name, file_type, file_url, status, chunk_count, created_at 
        FROM kb_documents 
        WHERE client_id = :client_id
        ORDER BY created_at DESC
    """)
    result = await db.execute(query, {"client_id": client_id_str})
    return {"documents": [dict(row._mapping) for row in result.fetchall()]}


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    if "user" in current_user:
        client_id = current_user["user"]["client_id"]
    else:
        client_id = current_user.get("client_id")
    
    # Fetch doc to ensure ownership and get file_url
    query = text("SELECT file_url FROM kb_documents WHERE id = :id AND client_id = :client_id")
    result = await db.execute(query, {"id": document_id, "client_id": client_id})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
        
    file_url = row.file_url
    
    # Delete from DB (chunks cascade automatically because of ON DELETE CASCADE)
    delete_query = text("DELETE FROM kb_documents WHERE id = :id")
    await db.execute(delete_query, {"id": document_id})
    await db.commit()
    
    # Delete from Supabase storage
    if file_url:
        try:
            supabase = get_supabase()
            parts = file_url.split('/kb-documents/')
            if len(parts) > 1:
                storage_path = parts[1]
                supabase.storage.from_("kb-documents").remove([storage_path])
        except Exception as e:
            print(f"Warning: Failed to delete file from storage: {e}")
            
    return {"message": "Document deleted successfully"}


class SearchRequest(BaseModel):
    query: str
    limit: int = 5

@router.post("/search")
async def search_kb(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if "user" in current_user:
        client_id = current_user["user"]["client_id"]
    else:
        client_id = current_user.get("client_id")
    
    # Use centralized KB service for search
    chunks = await kb_service.search_chunks(
        db=db,
        client_id=client_id,
        query=request.query,
        limit=request.limit
    )
    
    return {"results": chunks}


class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 10

@router.post("/crawl")
async def crawl_website_endpoint(
    request: CrawlRequest,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from app.services.crawler_service import crawl_website
    
    if "user" in current_user:
        client_id = current_user["user"]["client_id"]
    else:
        client_id = current_user.get("client_id")
    
    # Crawl the website
    try:
        pages = await crawl_website(request.url, max_pages=request.max_pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")
    
    if not pages:
        raise HTTPException(status_code=400, detail="No content found at the given URL.")
    
    total_chunks = 0
    document_ids = []
    
    try:
        for page in pages:
            page_content = page["content"]
            page_url = page["url"]
            page_title = page.get("title", page_url)
            
            if not page_content or len(page_content.strip()) < 50:
                continue
            
            # Chunk the text
            chunks = chunk_text(page_content)
            if not chunks:
                continue
            
            # Insert into kb_documents
            doc_query = text("""
                INSERT INTO kb_documents (client_id, file_name, file_type, file_url, status, chunk_count)
                VALUES (:client_id, :file_name, 'url', :file_url, 'processing', :chunk_count)
                RETURNING id
            """)
            doc_res = await db.execute(doc_query, {
                "client_id": client_id,
                "file_name": page_title[:255],
                "file_url": page_url,
                "chunk_count": len(chunks)
            })
            document_id = doc_res.scalar()
            document_ids.append(str(document_id))
            
            # Generate embeddings
            embeddings = embedding_service.generate_batch_embeddings(chunks)
            
            chunk_query = text("""
                INSERT INTO kb_chunks (client_id, document_id, content, embedding, metadata)
                VALUES (:client_id, :document_id, :content, :embedding, :metadata)
            """)
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                await db.execute(chunk_query, {
                    "client_id": client_id,
                    "document_id": document_id,
                    "content": chunk,
                    "embedding": str(embedding),
                    "metadata": json.dumps({"chunk_index": i, "source_url": page_url})
                })
            
            total_chunks += len(chunks)
            
            # Update document status to ready
            update_query = text("UPDATE kb_documents SET status = 'ready' WHERE id = :id")
            await db.execute(update_query, {"id": document_id})
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process crawled content: {str(e)}")
    
    return {
        "message": "success",
        "pages_crawled": len(pages),
        "documents_created": len(document_ids),
        "total_chunks": total_chunks,
        "document_ids": document_ids
    }

