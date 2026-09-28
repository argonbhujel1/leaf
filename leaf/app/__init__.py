import os
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory
from config import config
from app.extensions import db, login_manager, csrf


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Absolute paths so templates/static work on Vercel serverless
    _app_dir = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(_app_dir / 'templates'),
        static_folder=str(_app_dir / 'static'),
        instance_path=str(_app_dir.parent / 'instance'),
        instance_relative_config=False,
    )
    app.config.from_object(config.get(config_name, config['default']))

    # Vercel (and most serverless) filesystem is read-only except /tmp
    on_vercel = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    if on_vercel:
        tmp = Path('/tmp')
        app.config['UPLOAD_FOLDER'] = tmp / 'uploads'
        app.config['INSTANCE_PATH'] = str(tmp / 'instance')
        instance_path = tmp / 'instance'
    else:
        instance_path = Path(app.root_path).parent / 'instance'

    # Create dirs only where writable — never crash app startup
    try:
        instance_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        app.logger.warning('Could not create instance path: %s', e)

    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    for sub in ['products', 'gallery', 'news', 'logo', 'general']:
        try:
            (upload_folder / sub).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            app.logger.warning('Could not create upload dir %s: %s', sub, e)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models.settings import SiteSetting
        from app.models.product import ProductCategory
        from config import Config
        
        def get_setting(key, default=''):
            try:
                return SiteSetting.get(key, default)
            except Exception:
                return default
        
        categories = []
        try:
            categories = ProductCategory.query.filter_by(is_active=True).order_by(ProductCategory.sort_order).all()
        except Exception:
            pass
        return {
            'site_name': get_setting('site_name', Config.SITE_NAME),
            'site_tagline': get_setting('site_tagline', 'Quality Manufacturing. Reliable Products. Trusted Partnership.'),
            'site_logo': get_setting('site_logo', ''),
            'hms_login_url': Config.HMS_LOGIN_URL,
            'site_url': Config.SITE_URL,
            'contact_email': get_setting('contact_email', ''),
            'contact_phone': get_setting('contact_phone', ''),
            'contact_address': get_setting('contact_address', ''),
            'social_facebook': get_setting('social_facebook', ''),
            'social_linkedin': get_setting('social_linkedin', ''),
            'social_twitter': get_setting('social_twitter', ''),
            'social_instagram': get_setting('social_instagram', ''),
            'product_categories': categories,
            'get_setting': get_setting,
        }
    
    # Security headers
    @app.after_request
    def set_security_headers(response):
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            response.headers[header] = value
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    # Robots.txt and sitemap
    @app.route('/robots.txt')
    def robots():
        return send_from_directory(app.static_folder, 'robots.txt')
    
    @app.route('/sitemap.xml')
    def sitemap():
        from app.services.seo import generate_sitemap
        return generate_sitemap(), 200, {'Content-Type': 'application/xml'}
    
    # Create tables and seed (safe on serverless cold starts)
    with app.app_context():
        try:
            db.create_all()
            from app.services.seed import seed_default_data
            seed_default_data()
        except Exception as e:
            app.logger.warning('DB init/seed deferred: %s', e)
    
    return app
