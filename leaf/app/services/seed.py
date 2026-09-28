"""Seed default public content. No invented company facts - only placeholders."""
from app.extensions import db
from app.models.user import User
from app.models.settings import SiteSetting, PageContent, SEOSetting
from app.models.product import ProductCategory
from app.models.gallery import GalleryCategory
from app.models.news import NewsCategory


def seed_default_data():
    """Seed only if database is empty of essential data."""
    # Admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@leafletang.argan.com.np',
            full_name='Site Administrator',
            is_admin=True,
            is_active=True
        )
        admin.set_password('ChangeMeNow123!')
        db.session.add(admin)
    
    # Site settings - placeholders only
    defaults = [
        ('site_name', 'Leafletang Enterprises', 'text', 'general', 'Site Name'),
        ('site_tagline', 'Quality Manufacturing. Reliable Products. Trusted Partnership.', 'text', 'general', 'Site Tagline'),
        ('site_logo', '', 'image', 'general', 'Site Logo'),
        ('site_favicon', '', 'image', 'general', 'Favicon'),
        ('footer_text', 'Leafletang Enterprises. All rights reserved.', 'text', 'general', 'Footer Text'),
        ('contact_email', '', 'text', 'contact', 'Contact Email'),
        ('contact_phone', '', 'text', 'contact', 'Contact Phone'),
        ('contact_address', '', 'text', 'contact', 'Company Address'),
        ('contact_hours', '', 'text', 'contact', 'Business Hours'),
        ('google_maps_embed', '', 'text', 'contact', 'Google Maps Embed Code'),
        ('social_facebook', '', 'text', 'social', 'Facebook URL'),
        ('social_linkedin', '', 'text', 'social', 'LinkedIn URL'),
        ('social_twitter', '', 'text', 'social', 'Twitter/X URL'),
        ('social_instagram', '', 'text', 'social', 'Instagram URL'),
        ('hero_headline', 'Quality Manufacturing. Reliable Products. Trusted Partnership.', 'text', 'homepage', 'Hero Headline'),
        ('hero_subheadline', 'We manufacture quality products with precision and care for our valued partners.', 'text', 'homepage', 'Hero Subheadline'),
        ('hero_image', '', 'image', 'homepage', 'Hero Background Image'),
        ('about_intro', 'Leafletang Enterprises is a manufacturing company dedicated to producing quality products through our own factory facilities.', 'html', 'about', 'About Introduction'),
        ('about_mission', 'To deliver reliable, high-quality manufactured products that meet the needs of our customers and partners.', 'html', 'about', 'Mission'),
        ('about_vision', 'To be a trusted manufacturing partner known for quality, consistency, and integrity.', 'html', 'about', 'Vision'),
        ('about_values', 'Quality, Integrity, Reliability, Customer Focus, Continuous Improvement', 'text', 'about', 'Core Values'),
        ('about_philosophy', 'We believe in owning our manufacturing process from start to finish, ensuring control over quality at every stage.', 'html', 'about', 'Manufacturing Philosophy'),
        ('manufacturing_overview', 'Our manufacturing process follows a structured workflow designed for consistency and quality.', 'html', 'manufacturing', 'Manufacturing Overview'),
        ('manufacturing_workflow', 'Raw Materials → Production → Quality Inspection → Grading → Finished Product → Dispatch', 'text', 'manufacturing', 'Workflow Steps'),
        ('quality_intro', 'Quality is central to everything we produce. Our inspection and grading processes help ensure products meet expected standards.', 'html', 'quality', 'Quality Introduction'),
        ('quality_commitment', 'We are committed to maintaining consistent quality standards across our product range through systematic inspection and verification.', 'html', 'quality', 'Quality Commitment'),
    ]
    
    for key, value, vtype, group, label in defaults:
        if not SiteSetting.query.filter_by(key=key).first():
            db.session.add(SiteSetting(
                key=key, value=value, value_type=vtype, group=group, label=label
            ))
    
    # Page content sections
    page_sections = [
        ('home', 'hero', 'Welcome to Leafletang Enterprises',
         'Quality Manufacturing. Reliable Products. Trusted Partnership.'),
        ('home', 'intro', 'About Our Company',
         'Leafletang Enterprises operates its own manufacturing facilities, producing products with a focus on quality and reliability.'),
        ('home', 'cta', 'Ready to Partner With Us?',
         'Contact us to discuss your requirements and explore how we can work together.'),
        ('about', 'intro', 'Who We Are',
         'Leafletang Enterprises is a manufacturing company that owns and operates its factory to produce quality products.'),
        ('about', 'mission', 'Our Mission',
         'To deliver reliable, high-quality manufactured products that meet the needs of our customers and partners.'),
        ('about', 'vision', 'Our Vision',
         'To be a trusted manufacturing partner known for quality, consistency, and integrity.'),
        ('about', 'values', 'Core Values',
         'Quality • Integrity • Reliability • Customer Focus • Continuous Improvement'),
        ('manufacturing', 'overview', 'Our Manufacturing Process',
         'We follow a structured manufacturing workflow designed for consistency and quality control.'),
        ('manufacturing', 'workflow', 'Process Overview',
         'Raw Materials → Production → Quality Inspection → Grading → Finished Product → Dispatch'),
        ('quality', 'intro', 'Our Quality Approach',
         'Quality inspection and product grading are integral parts of our manufacturing process.'),
        ('quality', 'process', 'Quality Process',
         'We conduct systematic inspection, grading, and verification to maintain product standards.'),
        ('contact', 'intro', 'Get In Touch',
         'We welcome business inquiries and partnership opportunities. Reach out to discuss your requirements.'),
    ]
    
    for page, section, title, content in page_sections:
        if not PageContent.query.filter_by(page=page, section=section).first():
            db.session.add(PageContent(
                page=page, section=section, title=title, content=content, is_active=True
            ))
    
    # SEO defaults
    seo_pages = [
        ('home', 'Leafletang Enterprises | Quality Manufacturing',
         'Leafletang Enterprises manufactures quality products through its own factory. Explore our products and capabilities.'),
        ('about', 'About Us | Leafletang Enterprises',
         'Learn about Leafletang Enterprises, our mission, vision, and commitment to quality manufacturing.'),
        ('products', 'Products | Leafletang Enterprises',
         'Explore the range of products manufactured by Leafletang Enterprises.'),
        ('manufacturing', 'Manufacturing | Leafletang Enterprises',
         'Overview of our manufacturing process and capabilities.'),
        ('quality', 'Quality | Leafletang Enterprises',
         'Our approach to quality inspection, grading, and product verification.'),
        ('gallery', 'Gallery | Leafletang Enterprises',
         'View factory, production, and product images from Leafletang Enterprises.'),
        ('news', 'News & Updates | Leafletang Enterprises',
         'Latest news and updates from Leafletang Enterprises.'),
        ('contact', 'Contact Us | Leafletang Enterprises',
         'Get in touch with Leafletang Enterprises for business inquiries and partnerships.'),
    ]
    
    for page_key, title, desc in seo_pages:
        if not SEOSetting.query.filter_by(page_key=page_key).first():
            db.session.add(SEOSetting(
                page_key=page_key, title=title, description=desc,
                og_title=title, og_description=desc, robots='index, follow'
            ))
    
    # Default gallery categories
    gallery_cats = [
        ('Factory', 'factory', 'Factory facilities and infrastructure'),
        ('Production', 'production', 'Production processes and operations'),
        ('Products', 'products', 'Finished products'),
        ('Team', 'team', 'Our team'),
        ('Events', 'events', 'Company events and activities'),
    ]
    for name, slug, desc in gallery_cats:
        if not GalleryCategory.query.filter_by(slug=slug).first():
            db.session.add(GalleryCategory(name=name, slug=slug, description=desc, is_active=True))
    
    # Default news category
    if not NewsCategory.query.filter_by(slug='announcements').first():
        db.session.add(NewsCategory(name='Announcements', slug='announcements', is_active=True))
    
    # Placeholder product category (admin can edit/add real ones)
    if not ProductCategory.query.first():
        db.session.add(ProductCategory(
            name='General',
            slug='general',
            description='General product category. Edit or add categories via the admin panel.',
            is_active=True
        ))
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
