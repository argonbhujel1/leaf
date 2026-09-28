import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
from app.extensions import db
from app.models.media import MediaFile


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def optimize_image(filepath, max_width=1920, quality=85):
    """Optimize image for web display."""
    try:
        with Image.open(filepath) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if larger than max_width
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save optimized
            img.save(filepath, optimize=True, quality=quality)
            
            return img.width, img.height
    except Exception:
        return None, None


def create_thumbnail(filepath, thumb_path, size=(400, 400)):
    """Create a thumbnail."""
    try:
        with Image.open(filepath) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumb_path, optimize=True, quality=80)
            return True
    except Exception:
        return False


def save_upload(file, folder='general', create_thumb=False, user_id=None):
    """
    Save uploaded file securely.
    Returns relative path from uploads folder, or None on failure.
    """
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        return None
    
    original = secure_filename(file.filename)
    ext = original.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    
    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = upload_dir / unique_name
    file.save(str(filepath))
    
    width, height = None, None
    if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
        width, height = optimize_image(str(filepath))
        
        if create_thumb:
            thumb_name = f"thumb_{unique_name}"
            thumb_path = upload_dir / thumb_name
            create_thumbnail(str(filepath), str(thumb_path))
    
    # Record in media library
    relative_path = f"{folder}/{unique_name}"
    media = MediaFile(
        filename=unique_name,
        original_filename=original,
        file_path=relative_path,
        file_type='image' if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp', 'svg') else 'document',
        mime_type=file.content_type,
        file_size=filepath.stat().st_size if filepath.exists() else 0,
        width=width,
        height=height,
        folder=folder,
        uploaded_by=user_id
    )
    db.session.add(media)
    db.session.commit()
    
    return relative_path


def delete_upload(relative_path):
    """Delete an uploaded file."""
    if not relative_path:
        return False
    try:
        full_path = Path(current_app.config['UPLOAD_FOLDER']) / relative_path
        if full_path.exists():
            full_path.unlink()
        
        # Also try thumbnail
        parts = relative_path.rsplit('/', 1)
        if len(parts) == 2:
            thumb = Path(current_app.config['UPLOAD_FOLDER']) / parts[0] / f"thumb_{parts[1]}"
            if thumb.exists():
                thumb.unlink()
        
        # Remove from media library
        media = MediaFile.query.filter_by(file_path=relative_path).first()
        if media:
            db.session.delete(media)
            db.session.commit()
        
        return True
    except Exception:
        return False
