from datetime import datetime, timezone
from app.extensions import db
from slugify import slugify


class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    products = db.relationship('Product', back_populates='category', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name and not self.slug:
            self.slug = slugify(self.name)
    
    def __repr__(self):
        return f'<ProductCategory {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    product_code = db.Column(db.String(50), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    short_description = db.Column(db.Text)
    full_description = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON or newline-separated
    specifications = db.Column(db.Text)  # JSON or structured text
    available_grades = db.Column(db.String(255))  # Public grades only
    unit = db.Column(db.String(50))
    main_image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(300))
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime)
    
    category = db.relationship('ProductCategory', back_populates='products')
    images = db.relationship('ProductImage', back_populates='product',
                            cascade='all, delete-orphan', order_by='ProductImage.sort_order')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name and not self.slug:
            self.slug = slugify(self.name)
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    def __repr__(self):
        return f'<Product {self.name}>'


class ProductImage(db.Model):
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(200))
    caption = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    product = db.relationship('Product', back_populates='images')
    
    def __repr__(self):
        return f'<ProductImage {self.id}>'
