from datetime import datetime, timezone
from app.extensions import db
from slugify import slugify


class NewsCategory(db.Model):
    __tablename__ = 'news_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    posts = db.relationship('NewsPost', back_populates='category', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name and not self.slug:
            self.slug = slugify(self.name)
    
    def __repr__(self):
        return f'<NewsCategory {self.name}>'


class NewsPost(db.Model):
    __tablename__ = 'news_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(270), unique=True, nullable=False, index=True)
    cover_image = db.Column(db.String(255))
    short_description = db.Column(db.Text)
    content = db.Column(db.Text)
    author = db.Column(db.String(100), default='Leafletang Enterprises')
    category_id = db.Column(db.Integer, db.ForeignKey('news_categories.id'))
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))
    view_count = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    category = db.relationship('NewsCategory', back_populates='posts')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.title and not self.slug:
            self.slug = slugify(self.title)
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    def __repr__(self):
        return f'<NewsPost {self.title}>'
