from datetime import datetime, timezone
from app.extensions import db


class MediaFile(db.Model):
    __tablename__ = 'media_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # image, document
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    alt_text = db.Column(db.String(200))
    folder = db.Column(db.String(50), default='general')  # products, gallery, news, logo
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<MediaFile {self.filename}>'
