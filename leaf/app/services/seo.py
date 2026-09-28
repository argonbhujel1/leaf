from flask import url_for, current_app
from app.models.product import Product
from app.models.news import NewsPost
from app.models.settings import SEOSetting, SiteSetting
from datetime import datetime, timezone


def generate_sitemap():
    """Generate XML sitemap for public pages."""
    base_url = current_app.config.get('SITE_URL', 'https://leafletang.argan.com.np')
    
    urls = [
        {'loc': f'{base_url}/', 'priority': '1.0', 'changefreq': 'weekly'},
        {'loc': f'{base_url}/about', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f'{base_url}/products', 'priority': '0.9', 'changefreq': 'weekly'},
        {'loc': f'{base_url}/manufacturing', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': f'{base_url}/quality', 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': f'{base_url}/gallery', 'priority': '0.6', 'changefreq': 'weekly'},
        {'loc': f'{base_url}/news', 'priority': '0.8', 'changefreq': 'daily'},
        {'loc': f'{base_url}/contact', 'priority': '0.7', 'changefreq': 'monthly'},
    ]
    
    # Products
    products = Product.query.filter_by(status='published').all()
    for p in products:
        urls.append({
            'loc': f'{base_url}/products/{p.slug}',
            'priority': '0.8',
            'changefreq': 'weekly',
            'lastmod': p.updated_at.strftime('%Y-%m-%d') if p.updated_at else None
        })
    
    # News
    posts = NewsPost.query.filter_by(status='published').all()
    for post in posts:
        urls.append({
            'loc': f'{base_url}/news/{post.slug}',
            'priority': '0.7',
            'changefreq': 'monthly',
            'lastmod': post.updated_at.strftime('%Y-%m-%d') if post.updated_at else None
        })
    
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for u in urls:
        xml_parts.append('<url>')
        xml_parts.append(f'<loc>{u["loc"]}</loc>')
        if u.get('lastmod'):
            xml_parts.append(f'<lastmod>{u["lastmod"]}</lastmod>')
        xml_parts.append(f'<changefreq>{u.get("changefreq", "monthly")}</changefreq>')
        xml_parts.append(f'<priority>{u.get("priority", "0.5")}</priority>')
        xml_parts.append('</url>')
    
    xml_parts.append('</urlset>')
    return '\n'.join(xml_parts)


def get_organization_schema():
    """Generate Organization structured data - only with real data."""
    name = SiteSetting.get('site_name', 'Leafletang Enterprises')
    url = current_app.config.get('SITE_URL', 'https://leafletang.argan.com.np')
    email = SiteSetting.get('contact_email', '')
    phone = SiteSetting.get('contact_phone', '')
    address = SiteSetting.get('contact_address', '')
    logo = SiteSetting.get('site_logo', '')
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": url,
    }
    
    if logo:
        schema["logo"] = f"{url}/static/uploads/{logo}" if not logo.startswith('http') else logo
    if email:
        schema["email"] = email
    if phone:
        schema["telephone"] = phone
    if address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": address
        }
    
    return schema


def get_product_schema(product):
    """Generate Product structured data."""
    base_url = current_app.config.get('SITE_URL', 'https://leafletang.argan.com.np')
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": product.short_description or product.full_description or '',
        "url": f"{base_url}/products/{product.slug}",
    }
    if product.product_code:
        schema["sku"] = product.product_code
    if product.main_image:
        img = product.main_image
        schema["image"] = f"{base_url}/static/uploads/{img}" if not img.startswith('http') else img
    if product.category:
        schema["category"] = product.category.name
    return schema
