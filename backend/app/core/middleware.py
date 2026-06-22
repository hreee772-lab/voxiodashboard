from fastapi import Request, HTTPException, Depends
from app.core.security import verify_token

ADMIN_ONLY_PATHS = [
    "/api/v1/kb/upload",
    "/api/v1/kb/documents",
    "/api/v1/auth/team",
    "/api/v1/auth/team/invite",
    "/api/v1/auth/team/update",
    "/api/v1/auth/team/remove",
    "/api/v1/kb/crawl",
]

SPECIALIST_PATHS = [
    "/api/v1/tickets",
    "/api/v1/sessions",
    "/api/v1/calendar",
]

READ_ONLY_PATHS = [
    "/api/v1/sessions",
    "/api/v1/tickets",
]

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    # Check if payload contains 'user' object or top-level fields
    user_role = payload.get("role", "specialist")
    request_path = request.url.path
    request_method = request.method
    
    # Enforce admin-only paths
    if any(request_path.startswith(path) for path in ADMIN_ONLY_PATHS):
        if user_role not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Admin access required")
    
    # Enforce read-only for viewers
    if user_role == "viewer" and request_method in ["POST", "PUT", "PATCH", "DELETE"]:
        # Allow viewer to read but not write
        if any(request_path.startswith(path) for path in READ_ONLY_PATHS):
            raise HTTPException(status_code=403, detail="Viewers have read-only access")
    
    return payload

async def require_admin(current_user: dict = Depends(get_current_user)):
    role = current_user.get("role") or current_user.get("user", {}).get("role", "specialist")
    if role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
