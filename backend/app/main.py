import os
import uuid
import time
import shutil
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import UPLOAD_DIR, SECRET_SUBMIT_TOKEN, CLIENT_SECRET_SLUG, ADMIN_PASSWORD, TEAM_PASSWORD, HONORED_PERSON
from .database import (
    init_db,
    create_message,
    get_approved_messages,
    get_all_messages_for_admin,
    get_message_by_id,
    update_message_status,
    update_message_content,
    delete_message,
    get_stats
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Livre d'Or Dr Béatrice", lifespan=lifespan)

# Allow all CORS for ease of local dev and production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded media files directly in full resolution
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Security helpers
def verify_admin_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentification requise")
    parts = authorization.split()
    token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else authorization
    if token != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Mot de passe administrateur incorrect")
    return True

# Pydantic models for admin requests
class AdminLoginRequest(BaseModel):
    password: str

class StatusUpdateRequest(BaseModel):
    status: str  # 'approved', 'rejected', 'pending'

class MessageEditRequest(BaseModel):
    author_name: str
    pet_name: str
    pet_species: str
    years_known: str
    message: str

# ----------------- Public Endpoints -----------------

@app.get("/api/config")
def get_public_config():
    """Returns public configuration and doctor's name."""
    return {
        "doctor_name": HONORED_PERSON
    }

@app.get("/api/client-access/verify")
def verify_client_access(slug: str = Query("")):
    """Verifies if the client invitation slug matches the backend configuration."""
    is_valid = slug.strip().lower() == CLIENT_SECRET_SLUG.strip().lower()
    return {"valid": is_valid}

@app.get("/api/admin/config")
def get_admin_config(authorized: bool = Depends(verify_admin_token)):
    """Returns private admin configuration including current client submission slug."""
    return {
        "client_slug": CLIENT_SECRET_SLUG,
        "honored_person": HONORED_PERSON
    }

@app.get("/api/messages")
def list_approved_messages(species: Optional[str] = None):
    """Returns only approved messages for Dr Béatrice's tribute view."""
    return get_approved_messages(species_filter=species)
    return get_approved_messages(species_filter=species)

@app.post("/api/messages/submit")
async def submit_message(
    token: str = Form(...),
    author_name: str = Form(...),
    pet_name: str = Form(...),
    pet_species: str = Form("Autre"),
    years_known: str = Form(""),
    message: str = Form(...),
    website_url: Optional[str] = Form(None),       # Honeypot: must be empty
    form_started_at: Optional[float] = Form(None), # Timestamp in ms: anti-instant bot
    media: Optional[UploadFile] = File(None)
):
    """
    Submits a new guestbook message.
    - Validates URL token.
    - Filters automated bots with honeypot & submission timing.
    - Stores raw high-resolution media without degradation.
    - Saves with status='pending' for moderation.
    """
    # 1. Token validation
    if token.strip() != SECRET_SUBMIT_TOKEN:
        raise HTTPException(
            status_code=403, 
            detail="Le jeton d'accès au formulaire est invalide ou a expiré."
        )

    # 2. Honeypot check: robots fill hidden fields
    if website_url and website_url.strip():
        # Silently reject bots with fake success
        return {"success": True, "message": "Message reçu"}

    # 3. Form timing check: prevent instant spam scripts (< 1 second)
    if form_started_at:
        try:
            now_ms = time.time() * 1000
            diff_ms = now_ms - float(form_started_at)
            if diff_ms < 1200:  # less than 1.2s is bot activity
                return {"success": True, "message": "Message reçu"}
        except Exception:
            pass

    # 4. Input validation
    if not author_name.strip() or not pet_name.strip() or not message.strip():
        raise HTTPException(
            status_code=400, 
            detail="Veuillez remplir votre nom, le nom de votre animal et votre message."
        )

    # 5. Media file handling (high-res photos & videos)
    media_path = None
    media_type = None

    if media and media.filename:
        ext = Path(media.filename).suffix.lower()
        image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}
        video_exts = {".mp4", ".mov", ".webm", ".m4v"}

        if ext in image_exts:
            media_type = "image"
        elif ext in video_exts:
            media_type = "video"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Format de fichier non pris en charge ({ext}). Utilisez une photo (JPG, PNG, WEBP) ou une vidéo (MP4, MOV)."
            )

        unique_filename = f"{uuid.uuid4().hex}{ext}"
        target_path = UPLOAD_DIR / unique_filename

        with target_path.open("wb") as buffer:
            shutil.copyfileobj(media.file, buffer)

        media_path = f"/uploads/{unique_filename}"

    # 6. Store with status='pending'
    msg_id = create_message(
        author_name=author_name,
        pet_name=pet_name,
        pet_species=pet_species,
        years_known=years_known,
        message=message,
        media_path=media_path,
        media_type=media_type,
        status="pending"
    )

    return {
        "success": True,
        "id": msg_id,
        "message": "Votre message a bien été transmis et sera affiché dans le livre d'or après relecture par notre équipe !"
    }

@app.post("/api/team/upload")
async def upload_team_photos(
    password: str = Form(...),
    author_name: Optional[str] = Form("L'Équipe"),
    message: Optional[str] = Form(""),
    website_url: Optional[str] = Form(None),
    files: List[UploadFile] = File(...)
):
    """
    Uploads one or multiple team/party photos from clinic colleagues.
    Protected by clinic admin password and anti-bot verification.
    """
    # 1. Anti-bot honeypot check
    if website_url and website_url.strip():
        return {"success": True, "count": 0, "ids": []}

    # 2. Password verification (accepts team password or admin password)
    allowed_passwords = {p.strip() for p in (TEAM_PASSWORD, ADMIN_PASSWORD) if p}
    if not password or password.strip() not in allowed_passwords:
        raise HTTPException(
            status_code=403, 
            detail="Mot de passe équipe incorrect. Seule l'équipe autorisée peut importer des photos."
        )

    if not files:
        raise HTTPException(status_code=400, detail="Veuillez sélectionner au moins un fichier.")

    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}
    video_exts = {".mp4", ".mov", ".webm", ".m4v"}

    created_ids = []
    author = author_name.strip() if author_name and author_name.strip() else "L'Équipe"
    default_msg = message.strip() if message and message.strip() else "Souvenir d'équipe 📸"

    for file in files:
        if not file.filename:
            continue
        ext = Path(file.filename).suffix.lower()
        if ext in image_exts:
            media_type = "image"
        elif ext in video_exts:
            media_type = "video"
        else:
            continue

        unique_filename = f"team_{uuid.uuid4().hex}{ext}"
        target_path = UPLOAD_DIR / unique_filename

        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        media_path = f"/uploads/{unique_filename}"

        msg_id = create_message(
            author_name=author,
            pet_name="Équipe Clinique",
            pet_species="Équipe",
            years_known="Clinique",
            message=default_msg,
            media_path=media_path,
            media_type=media_type,
            status="approved"
        )
        created_ids.append(msg_id)

    if not created_ids:
        raise HTTPException(status_code=400, detail="Aucun fichier image ou vidéo valide n'a pu être traité.")

    return {
        "success": True,
        "count": len(created_ids),
        "ids": created_ids,
        "message": f"{len(created_ids)} photo(s) souvenir(s) ajoutée(s) avec succès !"
    }

# ----------------- Admin Endpoints -----------------

@app.post("/api/admin/login")
def admin_login(body: AdminLoginRequest):
    if body.password == ADMIN_PASSWORD:
        return {"success": True, "token": ADMIN_PASSWORD}
    raise HTTPException(status_code=401, detail="Mot de passe incorrect")

@app.get("/api/admin/messages")
def admin_list_messages(status: Optional[str] = None, authorized: bool = Depends(verify_admin_token)):
    messages = get_all_messages_for_admin(status=status)
    stats = get_stats()
    return {
        "stats": stats,
        "messages": messages
    }

@app.patch("/api/admin/messages/{message_id}/status")
def admin_update_status(message_id: int, body: StatusUpdateRequest, authorized: bool = Depends(verify_admin_token)):
    valid_statuses = {"pending", "approved", "rejected"}
    if body.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Statut invalide")
    updated = update_message_status(message_id, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Message introuvable")
    return {"success": True, "id": message_id, "status": body.status}

@app.put("/api/admin/messages/{message_id}")
def admin_edit_message(message_id: int, body: MessageEditRequest, authorized: bool = Depends(verify_admin_token)):
    updated = update_message_content(
        message_id=message_id,
        author_name=body.author_name,
        pet_name=body.pet_name,
        pet_species=body.pet_species,
        years_known=body.years_known,
        message=body.message
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Message introuvable")
    return {"success": True, "id": message_id}

@app.delete("/api/admin/messages/{message_id}")
def admin_delete_message(message_id: int, authorized: bool = Depends(verify_admin_token)):
    media_path = delete_message(message_id)
    # Cleanup physical media file if present
    if media_path and media_path.startswith("/uploads/"):
        filename = media_path.replace("/uploads/", "")
        file_disk_path = UPLOAD_DIR / filename
        if file_disk_path.exists():
            try:
                file_disk_path.unlink()
            except Exception:
                pass
    return {"success": True, "id": message_id}

# In production / Docker, serve built Svelte SPA files
from .config import FRONTEND_DIST_DIR
if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name="frontend")

