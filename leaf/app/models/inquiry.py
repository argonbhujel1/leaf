from datetime import datetime, timezone
from app.extensions import db


class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(150))
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    product_service = db.Column(db.String(200))
    quantity = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new, read, replied, archived
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(300))
    notes = db.Column(db.Text)  # Admin notes
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Inquiry {self.name} - {self.email}>'
