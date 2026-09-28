from datetime import datetime, timezone
from app.extensions import db
from slugify import slugify


class GalleryCategory(db.Model):
    __tablename__ = 'gallery_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    items = db.relationship('GalleryItem', back_populates='category', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name and not self.slug:
            self.slug = slugify(self.name)
    
    def __repr__(self):
        return f'<GalleryCategory {self.name}>'


class GalleryItem(db.Model):
    __tablename__ = 'gallery_items'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255), nullable=False)
    thumbnail_path = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('gallery_categories.id'))
    sort_order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    alt_text = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    category = db.relationship('GalleryCategory', back_populates='items')
    
    def __repr__(self):
        return f'<GalleryItem {self.title}>'
