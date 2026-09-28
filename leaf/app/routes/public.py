from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from app.extensions import db
from app.models.product import Product, ProductCategory
from app.models.gallery import GalleryItem, GalleryCategory
from app.models.news import NewsPost, NewsCategory
from app.models.inquiry import Inquiry
from app.models.settings import SiteSetting, PageContent, SEOSetting
from app.services.seo import get_organization_schema, get_product_schema
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
import bleach

public_bp = Blueprint('public', __name__)


class InquiryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=120)])
    company = StringField('Company', validators=[Optional(), Length(max=150)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=50)])
    product_service = StringField('Product / Service', validators=[Optional(), Length(max=200)])
    quantity = StringField('Quantity', validators=[Optional(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=5000)])
    submit = SubmitField('Submit Inquiry')


def get_seo(page_key):
    return SEOSetting.get_for_page(page_key)


def get_page_content(page, section):
    return PageContent.get_section(page, section)


@public_bp.route('/')
def home():
    seo = get_seo('home')
    featured_products = Product.query.filter_by(status='published', is_featured=True)\
        .order_by(Product.sort_order).limit(6).all()
    latest_news = NewsPost.query.filter_by(status='published')\
        .order_by(NewsPost.published_at.desc()).limit(3).all()
    featured_gallery = GalleryItem.query.filter_by(is_active=True, is_featured=True)\
        .order_by(GalleryItem.sort_order).limit(6).all()
    
    return render_template('public/home.html',
                           seo=seo,
                           hero_headline=SiteSetting.get('hero_headline'),
                           hero_subheadline=SiteSetting.get('hero_subheadline'),
                           hero_image=SiteSetting.get('hero_image'),
                           featured_products=featured_products,
                           latest_news=latest_news,
                           featured_gallery=featured_gallery,
                           intro=get_page_content('home', 'intro'),
                           cta=get_page_content('home', 'cta'),
                           org_schema=get_organization_schema())


@public_bp.route('/about')
def about():
    seo = get_seo('about')
    sections = {
        'intro': get_page_content('about', 'intro'),
        'mission': get_page_content('about', 'mission'),
        'vision': get_page_content('about', 'vision'),
        'values': get_page_content('about', 'values'),
    }
    return render_template('public/about.html', seo=seo, sections=sections,
                           about_intro=SiteSetting.get('about_intro'),
                           about_mission=SiteSetting.get('about_mission'),
                           about_vision=SiteSetting.get('about_vision'),
                           about_values=SiteSetting.get('about_values'),
                           about_philosophy=SiteSetting.get('about_philosophy'))


@public_bp.route('/products')
def products():
    seo = get_seo('products')
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category', '')
    search = request.args.get('q', '').strip()
    
    query = Product.query.filter_by(status='published')
    
    active_category = None
    if category_slug:
        active_category = ProductCategory.query.filter_by(slug=category_slug, is_active=True).first()
        if active_category:
            query = query.filter_by(category_id=active_category.id)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.short_description.ilike(search_term),
                Product.product_code.ilike(search_term)
            )
        )
    
    pagination = query.order_by(Product.sort_order, Product.name)\
        .paginate(page=page, per_page=current_app.config['PRODUCTS_PER_PAGE'], error_out=False)
    
    categories = ProductCategory.query.filter_by(is_active=True)\
        .order_by(ProductCategory.sort_order).all()
    
    return render_template('public/products.html',
                           seo=seo,
                           products=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           active_category=active_category,
                           search=search)


@public_bp.route('/products/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, status='published').first_or_404()
    product.view_count = (product.view_count or 0) + 1
    db.session.commit()
    
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == 'published'
    ).limit(4).all()
    
    return render_template('public/product_detail.html',
                           product=product,
                           related=related,
                           product_schema=get_product_schema(product),
                           seo_title=product.seo_title or product.name,
                           seo_description=product.seo_description or product.short_description)


@public_bp.route('/manufacturing')
def manufacturing():
    seo = get_seo('manufacturing')
    return render_template('public/manufacturing.html',
                           seo=seo,
                           overview=SiteSetting.get('manufacturing_overview'),
                           workflow=SiteSetting.get('manufacturing_workflow'),
                           overview_section=get_page_content('manufacturing', 'overview'),
                           workflow_section=get_page_content('manufacturing', 'workflow'))


@public_bp.route('/quality')
def quality():
    seo = get_seo('quality')
    return render_template('public/quality.html',
                           seo=seo,
                           intro=SiteSetting.get('quality_intro'),
                           commitment=SiteSetting.get('quality_commitment'),
                           intro_section=get_page_content('quality', 'intro'),
                           process_section=get_page_content('quality', 'process'))


@public_bp.route('/gallery')
def gallery():
    seo = get_seo('gallery')
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category', '')
    
    query = GalleryItem.query.filter_by(is_active=True)
    active_category = None
    
    if category_slug:
        active_category = GalleryCategory.query.filter_by(slug=category_slug, is_active=True).first()
        if active_category:
            query = query.filter_by(category_id=active_category.id)
    
    pagination = query.order_by(GalleryItem.sort_order, GalleryItem.created_at.desc())\
        .paginate(page=page, per_page=current_app.config['GALLERY_PER_PAGE'], error_out=False)
    
    categories = GalleryCategory.query.filter_by(is_active=True)\
        .order_by(GalleryCategory.sort_order).all()
    
    return render_template('public/gallery.html',
                           seo=seo,
                           items=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           active_category=active_category)


@public_bp.route('/news')
def news():
    seo = get_seo('news')
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category', '')
    search = request.args.get('q', '').strip()
    
    query = NewsPost.query.filter_by(status='published')
    active_category = None
    
    if category_slug:
        active_category = NewsCategory.query.filter_by(slug=category_slug, is_active=True).first()
        if active_category:
            query = query.filter_by(category_id=active_category.id)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                NewsPost.title.ilike(search_term),
                NewsPost.short_description.ilike(search_term)
            )
        )
    
    pagination = query.order_by(NewsPost.published_at.desc())\
        .paginate(page=page, per_page=current_app.config['NEWS_PER_PAGE'], error_out=False)
    
    categories = NewsCategory.query.filter_by(is_active=True)\
        .order_by(NewsCategory.sort_order).all()
    
    return render_template('public/news.html',
                           seo=seo,
                           posts=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           active_category=active_category,
                           search=search)


@public_bp.route('/news/<slug>')
def news_detail(slug):
    post = NewsPost.query.filter_by(slug=slug, status='published').first_or_404()
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()
    
    related = NewsPost.query.filter(
        NewsPost.id != post.id,
        NewsPost.status == 'published'
    ).order_by(NewsPost.published_at.desc()).limit(3).all()
    
    return render_template('public/news_detail.html',
                           post=post,
                           related=related,
                           seo_title=post.seo_title or post.title,
                           seo_description=post.seo_description or post.short_description)


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    seo = get_seo('contact')
    form = InquiryForm()
    
    if form.validate_on_submit():
        # Sanitize inputs
        inquiry = Inquiry(
            name=bleach.clean(form.name.data.strip()),
            company=bleach.clean(form.company.data.strip()) if form.company.data else None,
            email=form.email.data.strip().lower(),
            phone=bleach.clean(form.phone.data.strip()) if form.phone.data else None,
            product_service=bleach.clean(form.product_service.data.strip()) if form.product_service.data else None,
            quantity=bleach.clean(form.quantity.data.strip()) if form.quantity.data else None,
            message=bleach.clean(form.message.data.strip()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:300] if request.user_agent else None
        )
        db.session.add(inquiry)
        db.session.commit()

        # Notify admin by email (form still succeeds if mail fails)
        try:
            from app.services.email import send_inquiry_notification
            send_inquiry_notification(inquiry)
        except Exception as e:
            current_app.logger.warning('Inquiry email error: %s', e)

        flash('Thank you for your inquiry. We will get back to you soon.', 'success')
        return redirect(url_for('public.contact'))
    
    return render_template('public/contact.html',
                           seo=seo,
                           form=form,
                           intro=get_page_content('contact', 'intro'),
                           contact_email=SiteSetting.get('contact_email'),
                           contact_phone=SiteSetting.get('contact_phone'),
                           contact_address=SiteSetting.get('contact_address'),
                           contact_hours=SiteSetting.get('contact_hours'),
                           google_maps=SiteSetting.get('google_maps_embed'))
