from datetime import datetime, timezone
from app.extensions import db


class SiteSetting(db.Model):
    """Key-value store for site-wide settings."""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='text')  # text, html, json, boolean, image
    group = db.Column(db.String(50), default='general')  # general, contact, social, homepage, about, etc.
    label = db.Column(db.String(150))
    description = db.Column(db.String(300))
    sort_order = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<SiteSetting {self.key}>'
    
    @classmethod
    def get(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            if setting.value_type == 'boolean':
                return setting.value in ('true', '1', 'yes', True)
            return setting.value
        return default
    
    @classmethod
    def set(cls, key, value, value_type='text', group='general', label=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value) if value is not None else None
            setting.value_type = value_type
            setting.updated_at = datetime.now(timezone.utc)
        else:
            setting = cls(
                key=key,
                value=str(value) if value is not None else None,
                value_type=value_type,
                group=group,
                label=label or key.replace('_', ' ').title()
            )
            db.session.add(setting)
        db.session.commit()
        return setting


class PageContent(db.Model):
    """Editable page content blocks."""
    __tablename__ = 'page_contents'
    
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(50), nullable=False, index=True)  # home, about, manufacturing, quality, contact
    section = db.Column(db.String(50), nullable=False)  # hero, intro, mission, etc.
    title = db.Column(db.String(250))
    content = db.Column(db.Text)
    image = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    meta_data = db.Column(db.Text)  # JSON for extra fields
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('page', 'section', name='uq_page_section'),
    )
    
    def __repr__(self):
        return f'<PageContent {self.page}.{self.section}>'
    
    @classmethod
    def get_section(cls, page, section, default=None):
        item = cls.query.filter_by(page=page, section=section, is_active=True).first()
        return item if item else default


class SEOSetting(db.Model):
    """Per-page SEO settings."""
    __tablename__ = 'seo_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    page_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))
    keywords = db.Column(db.String(300))
    og_title = db.Column(db.String(200))
    og_description = db.Column(db.String(300))
    og_image = db.Column(db.String(255))
    canonical_url = db.Column(db.String(300))
    robots = db.Column(db.String(50), default='index, follow')
    structured_data = db.Column(db.Text)  # JSON-LD
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<SEOSetting {self.page_key}>'
    
    @classmethod
    def get_for_page(cls, page_key):
        return cls.query.filter_by(page_key=page_key).first()
