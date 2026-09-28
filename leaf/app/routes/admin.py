from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.product import Product, ProductCategory, ProductImage
from app.models.gallery import GalleryItem, GalleryCategory
from app.models.news import NewsPost, NewsCategory
from app.models.inquiry import Inquiry
from app.models.settings import SiteSetting, PageContent, SEOSetting
from app.services.uploads import save_upload, delete_upload
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, SelectField, BooleanField,
                     SubmitField, IntegerField, HiddenField)
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from slugify import slugify
import bleach

admin_bp = Blueprint('admin', __name__)


# ---------- Forms ----------
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    product_code = StringField('Product Code', validators=[Optional(), Length(max=50)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    short_description = TextAreaField('Short Description', validators=[Optional()])
    full_description = TextAreaField('Full Description', validators=[Optional()])
    features = TextAreaField('Features (one per line)', validators=[Optional()])
    specifications = TextAreaField('Specifications', validators=[Optional()])
    available_grades = StringField('Available Grades (public)', validators=[Optional(), Length(max=255)])
    unit = StringField('Unit', validators=[Optional(), Length(max=50)])
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')])
    is_featured = BooleanField('Featured')
    sort_order = IntegerField('Sort Order', default=0)
    seo_title = StringField('SEO Title', validators=[Optional(), Length(max=200)])
    seo_description = TextAreaField('SEO Description', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Save Product')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    sort_order = IntegerField('Sort Order', default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')


class NewsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=250)])
    short_description = TextAreaField('Short Description', validators=[Optional()])
    content = TextAreaField('Content', validators=[Optional()])
    author = StringField('Author', validators=[Optional(), Length(max=100)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')])
    is_featured = BooleanField('Featured')
    seo_title = StringField('SEO Title', validators=[Optional(), Length(max=200)])
    seo_description = TextAreaField('SEO Description', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Save')


class GalleryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    sort_order = IntegerField('Sort Order', default=0)
    is_featured = BooleanField('Featured')
    is_active = BooleanField('Active', default=True)
    alt_text = StringField('Alt Text', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save')


class SettingForm(FlaskForm):
    value = TextAreaField('Value', validators=[Optional()])
    submit = SubmitField('Save')


class PageContentForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=250)])
    content = TextAreaField('Content', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')


# ---------- Auth ----------
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


# ---------- Dashboard ----------
@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'products': Product.query.count(),
        'published_products': Product.query.filter_by(status='published').count(),
        'news': NewsPost.query.count(),
        'gallery': GalleryItem.query.count(),
        'inquiries_new': Inquiry.query.filter_by(status='new').count(),
        'inquiries_total': Inquiry.query.count(),
    }
    recent_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_inquiries=recent_inquiries)


# ---------- Products ----------
@admin_bp.route('/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Product.query
    if status:
        query = query.filter_by(status=status)
    pagination = query.order_by(Product.updated_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/products/list.html', products=pagination.items, pagination=pagination, status=status)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def product_new():
    form = ProductForm()
    form.category_id.choices = [(0, '-- Select --')] + [
        (c.id, c.name) for c in ProductCategory.query.order_by(ProductCategory.name).all()
    ]
    
    if form.validate_on_submit():
        product = Product(
            name=bleach.clean(form.name.data),
            product_code=form.product_code.data or None,
            category_id=form.category_id.data if form.category_id.data else None,
            short_description=bleach.clean(form.short_description.data) if form.short_description.data else None,
            full_description=bleach.clean(form.full_description.data) if form.full_description.data else None,
            features=form.features.data,
            specifications=form.specifications.data,
            available_grades=form.available_grades.data,
            unit=form.unit.data,
            status=form.status.data,
            is_featured=form.is_featured.data,
            sort_order=form.sort_order.data or 0,
            seo_title=form.seo_title.data,
            seo_description=form.seo_description.data,
            slug=slugify(form.name.data)
        )
        if form.status.data == 'published':
            product.published_at = datetime.now(timezone.utc)
        
        # Handle image upload
        if 'main_image' in request.files:
            f = request.files['main_image']
            if f and f.filename:
                path = save_upload(f, folder='products', user_id=current_user.id)
                if path:
                    product.main_image = path
        
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully.', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/products/form.html', form=form, product=None)


@admin_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(0, '-- Select --')] + [
        (c.id, c.name) for c in ProductCategory.query.order_by(ProductCategory.name).all()
    ]
    
    if form.validate_on_submit():
        product.name = bleach.clean(form.name.data)
        product.product_code = form.product_code.data or None
        product.category_id = form.category_id.data if form.category_id.data else None
        product.short_description = bleach.clean(form.short_description.data) if form.short_description.data else None
        product.full_description = bleach.clean(form.full_description.data) if form.full_description.data else None
        product.features = form.features.data
        product.specifications = form.specifications.data
        product.available_grades = form.available_grades.data
        product.unit = form.unit.data
        product.status = form.status.data
        product.is_featured = form.is_featured.data
        product.sort_order = form.sort_order.data or 0
        product.seo_title = form.seo_title.data
        product.seo_description = form.seo_description.data
        product.slug = slugify(form.name.data)
        
        if form.status.data == 'published' and not product.published_at:
            product.published_at = datetime.now(timezone.utc)
        
        if 'main_image' in request.files:
            f = request.files['main_image']
            if f and f.filename:
                if product.main_image:
                    delete_upload(product.main_image)
                path = save_upload(f, folder='products', user_id=current_user.id)
                if path:
                    product.main_image = path
        
        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin.products'))
    
    form.category_id.data = product.category_id or 0
    return render_template('admin/products/form.html', form=form, product=product)


@admin_bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def product_delete(id):
    product = Product.query.get_or_404(id)
    if product.main_image:
        delete_upload(product.main_image)
    for img in product.images:
        delete_upload(img.image_path)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin.products'))


# ---------- Categories ----------
@admin_bp.route('/categories')
@login_required
def categories():
    cats = ProductCategory.query.order_by(ProductCategory.sort_order).all()
    return render_template('admin/categories/list.html', categories=cats)


@admin_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def category_new():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = ProductCategory(
            name=bleach.clean(form.name.data),
            description=form.description.data,
            sort_order=form.sort_order.data or 0,
            is_active=form.is_active.data,
            slug=slugify(form.name.data)
        )
        db.session.add(cat)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/categories/form.html', form=form, category=None)


@admin_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def category_edit(id):
    cat = ProductCategory.query.get_or_404(id)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = bleach.clean(form.name.data)
        cat.description = form.description.data
        cat.sort_order = form.sort_order.data or 0
        cat.is_active = form.is_active.data
        cat.slug = slugify(form.name.data)
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/categories/form.html', form=form, category=cat)


@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def category_delete(id):
    cat = ProductCategory.query.get_or_404(id)
    if cat.products.count() > 0:
        flash('Cannot delete category with products. Reassign products first.', 'error')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories'))


# ---------- News ----------
@admin_bp.route('/news')
@login_required
def news_list():
    page = request.args.get('page', 1, type=int)
    pagination = NewsPost.query.order_by(NewsPost.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/news/list.html', posts=pagination.items, pagination=pagination)


@admin_bp.route('/news/new', methods=['GET', 'POST'])
@login_required
def news_new():
    form = NewsForm()
    form.category_id.choices = [(0, '-- Select --')] + [
        (c.id, c.name) for c in NewsCategory.query.order_by(NewsCategory.name).all()
    ]
    if form.validate_on_submit():
        post = NewsPost(
            title=bleach.clean(form.title.data),
            short_description=bleach.clean(form.short_description.data) if form.short_description.data else None,
            content=bleach.clean(form.content.data) if form.content.data else None,
            author=form.author.data or 'Leafletang Enterprises',
            category_id=form.category_id.data if form.category_id.data else None,
            status=form.status.data,
            is_featured=form.is_featured.data,
            seo_title=form.seo_title.data,
            seo_description=form.seo_description.data,
            slug=slugify(form.title.data)
        )
        if form.status.data == 'published':
            post.published_at = datetime.now(timezone.utc)
        
        if 'cover_image' in request.files:
            f = request.files['cover_image']
            if f and f.filename:
                path = save_upload(f, folder='news', user_id=current_user.id)
                if path:
                    post.cover_image = path
        
        db.session.add(post)
        db.session.commit()
        flash('News post created.', 'success')
        return redirect(url_for('admin.news_list'))
    return render_template('admin/news/form.html', form=form, post=None)


@admin_bp.route('/news/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    post = NewsPost.query.get_or_404(id)
    form = NewsForm(obj=post)
    form.category_id.choices = [(0, '-- Select --')] + [
        (c.id, c.name) for c in NewsCategory.query.order_by(NewsCategory.name).all()
    ]
    if form.validate_on_submit():
        post.title = bleach.clean(form.title.data)
        post.short_description = bleach.clean(form.short_description.data) if form.short_description.data else None
        post.content = bleach.clean(form.content.data) if form.content.data else None
        post.author = form.author.data or 'Leafletang Enterprises'
        post.category_id = form.category_id.data if form.category_id.data else None
        post.status = form.status.data
        post.is_featured = form.is_featured.data
        post.seo_title = form.seo_title.data
        post.seo_description = form.seo_description.data
        post.slug = slugify(form.title.data)
        if form.status.data == 'published' and not post.published_at:
            post.published_at = datetime.now(timezone.utc)
        
        if 'cover_image' in request.files:
            f = request.files['cover_image']
            if f and f.filename:
                if post.cover_image:
                    delete_upload(post.cover_image)
                path = save_upload(f, folder='news', user_id=current_user.id)
                if path:
                    post.cover_image = path
        
        db.session.commit()
        flash('News post updated.', 'success')
        return redirect(url_for('admin.news_list'))
    form.category_id.data = post.category_id or 0
    return render_template('admin/news/form.html', form=form, post=post)


@admin_bp.route('/news/<int:id>/delete', methods=['POST'])
@login_required
def news_delete(id):
    post = NewsPost.query.get_or_404(id)
    if post.cover_image:
        delete_upload(post.cover_image)
    db.session.delete(post)
    db.session.commit()
    flash('News post deleted.', 'success')
    return redirect(url_for('admin.news_list'))


# ---------- Gallery ----------
@admin_bp.route('/gallery')
@login_required
def gallery_list():
    page = request.args.get('page', 1, type=int)
    pagination = GalleryItem.query.order_by(GalleryItem.sort_order).paginate(page=page, per_page=24, error_out=False)
    return render_template('admin/gallery/list.html', items=pagination.items, pagination=pagination)


@admin_bp.route('/gallery/new', methods=['GET', 'POST'])
@login_required
def gallery_new():
    form = GalleryForm()
    form.category_id.choices = [(0, '-- Select --')] + [
        (c.id, c.name) for c in GalleryCategory.query.order_by(GalleryCategory.name).all()
    ]
    if form.validate_on_submit():
        if 'image' not in request.files or not request.files['image'].filename:
            flash('Image is required.', 'error')
            return render_template('admin/gallery/form.html', form=form, item=None)
        
        path = save_upload(request.files['image'], folder='gallery', create_thumb=True, user_id=current_user.id)
        if not path:
            flash('Invalid image file.', 'error')
            return render_template('admin/gallery/form.html', form=form, item=None)
        
        item = GalleryItem(
            title=bleach.clean(form.title.data),
            description=form.description.data,
            image_path=path,
            category_id=form.category_id.data if form.category_id.data else None,
            sort_order=form.sort_order.data or 0,
            is_featured=form.is_featured.data,
            is_active=form.is_active.data,
            alt_text=form.alt_text.data or form.title.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Gallery item added.', 'success')
        return redirect(url_for('admin.gallery_list'))
    return render_template('admin/gallery/form.html', form=form, item=None)


@admin_bp.route('/gallery/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def gallery_edit(id):
    item = GalleryItem.query.get_or_404(id)
    form = GalleryForm(obj=item)
    form.category_id.choices = [(0, '-- Select --')] + [
        (c.id, c.name) for c in GalleryCategory.query.order_by(GalleryCategory.name).all()
    ]
    if form.validate_on_submit():
        item.title = bleach.clean(form.title.data)
        item.description = form.description.data
        item.category_id = form.category_id.data if form.category_id.data else None
        item.sort_order = form.sort_order.data or 0
        item.is_featured = form.is_featured.data
        item.is_active = form.is_active.data
        item.alt_text = form.alt_text.data or form.title.data
        
        if 'image' in request.files and request.files['image'].filename:
            if item.image_path:
                delete_upload(item.image_path)
            path = save_upload(request.files['image'], folder='gallery', create_thumb=True, user_id=current_user.id)
            if path:
                item.image_path = path
        
        db.session.commit()
        flash('Gallery item updated.', 'success')
        return redirect(url_for('admin.gallery_list'))
    form.category_id.data = item.category_id or 0
    return render_template('admin/gallery/form.html', form=form, item=item)


@admin_bp.route('/gallery/<int:id>/delete', methods=['POST'])
@login_required
def gallery_delete(id):
    item = GalleryItem.query.get_or_404(id)
    if item.image_path:
        delete_upload(item.image_path)
    db.session.delete(item)
    db.session.commit()
    flash('Gallery item deleted.', 'success')
    return redirect(url_for('admin.gallery_list'))


# ---------- Inquiries ----------
@admin_bp.route('/inquiries')
@login_required
def inquiries():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Inquiry.query
    if status:
        query = query.filter_by(status=status)
    pagination = query.order_by(Inquiry.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/inquiries/list.html', inquiries=pagination.items, pagination=pagination, status=status)


@admin_bp.route('/inquiries/<int:id>')
@login_required
def inquiry_detail(id):
    inquiry = Inquiry.query.get_or_404(id)
    if inquiry.status == 'new':
        inquiry.status = 'read'
        db.session.commit()
    return render_template('admin/inquiries/detail.html', inquiry=inquiry)


@admin_bp.route('/inquiries/<int:id>/status', methods=['POST'])
@login_required
def inquiry_status(id):
    inquiry = Inquiry.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ('new', 'read', 'replied', 'archived'):
        inquiry.status = new_status
        db.session.commit()
        flash('Status updated.', 'success')
    return redirect(url_for('admin.inquiry_detail', id=id))


# ---------- Settings ----------
@admin_bp.route('/settings')
@login_required
def settings():
    groups = {}
    for s in SiteSetting.query.order_by(SiteSetting.group, SiteSetting.sort_order).all():
        groups.setdefault(s.group, []).append(s)
    return render_template('admin/settings/list.html', groups=groups)


@admin_bp.route('/settings/<key>', methods=['GET', 'POST'])
@login_required
def setting_edit(key):
    setting = SiteSetting.query.filter_by(key=key).first_or_404()
    form = SettingForm(value=setting.value)
    
    if form.validate_on_submit():
        if setting.value_type == 'image' and 'image' in request.files:
            f = request.files['image']
            if f and f.filename:
                if setting.value:
                    delete_upload(setting.value)
                path = save_upload(f, folder='logo' if 'logo' in key else 'general', user_id=current_user.id)
                if path:
                    setting.value = path
        else:
            setting.value = form.value.data
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings/edit.html', form=form, setting=setting)


# ---------- Page Content ----------
@admin_bp.route('/pages')
@login_required
def pages():
    contents = PageContent.query.order_by(PageContent.page, PageContent.sort_order).all()
    by_page = {}
    for c in contents:
        by_page.setdefault(c.page, []).append(c)
    return render_template('admin/pages/list.html', by_page=by_page)


@admin_bp.route('/pages/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def page_edit(id):
    content = PageContent.query.get_or_404(id)
    form = PageContentForm(obj=content)
    if form.validate_on_submit():
        content.title = form.title.data
        content.content = form.content.data
        content.is_active = form.is_active.data
        db.session.commit()
        flash('Page content updated.', 'success')
        return redirect(url_for('admin.pages'))
    return render_template('admin/pages/edit.html', form=form, content=content)


# ---------- SEO ----------
@admin_bp.route('/seo')
@login_required
def seo_list():
    settings = SEOSetting.query.order_by(SEOSetting.page_key).all()
    return render_template('admin/seo/list.html', settings=settings)


@admin_bp.route('/seo/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def seo_edit(id):
    setting = SEOSetting.query.get_or_404(id)
    if request.method == 'POST':
        setting.title = request.form.get('title', '')
        setting.description = request.form.get('description', '')
        setting.keywords = request.form.get('keywords', '')
        setting.og_title = request.form.get('og_title', '')
        setting.og_description = request.form.get('og_description', '')
        setting.robots = request.form.get('robots', 'index, follow')
        db.session.commit()
        flash('SEO settings updated.', 'success')
        return redirect(url_for('admin.seo_list'))
    return render_template('admin/seo/edit.html', setting=setting)
