"""Email notification helpers (stdlib smtplib — no extra dependency)."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def _mail_config():
    return {
        'server': os.environ.get('MAIL_SERVER', ''),
        'port': int(os.environ.get('MAIL_PORT', 587)),
        'use_tls': os.environ.get('MAIL_USE_TLS', 'true').lower() in ('1', 'true', 'yes'),
        'username': os.environ.get('MAIL_USERNAME', ''),
        'password': os.environ.get('MAIL_PASSWORD', ''),
        'default_sender': os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME', ''),
        'admin_email': os.environ.get('ADMIN_EMAIL') or '',
    }


def send_inquiry_notification(inquiry):
    """
    Send new contact/inquiry notification to admin email.
    Fails silently (logs warning) so form submit still succeeds if mail is misconfigured.
    """
    cfg = _mail_config()
    to_addr = cfg['admin_email'] or current_app.config.get('ADMIN_EMAIL', '')

    # Prefer site setting contact_email as fallback recipient
    if not to_addr:
        try:
            from app.models.settings import SiteSetting
            to_addr = SiteSetting.get('contact_email') or ''
        except Exception:
            pass

    if not cfg['server'] or not to_addr or not cfg['default_sender']:
        current_app.logger.warning(
            'Inquiry email skipped: MAIL_SERVER / ADMIN_EMAIL / MAIL_DEFAULT_SENDER not configured'
        )
        return False

    site_name = current_app.config.get('SITE_NAME', 'Leafletang Enterprises')
    subject = f'[{site_name}] New inquiry from {inquiry.name}'

    body_lines = [
        f'New contact inquiry received on {site_name}.',
        '',
        f'Name:     {inquiry.name}',
        f'Company:  {inquiry.company or "—"}',
        f'Email:    {inquiry.email}',
        f'Phone:    {inquiry.phone or "—"}',
        f'Product:  {inquiry.product_service or "—"}',
        f'Quantity: {inquiry.quantity or "—"}',
        '',
        'Message:',
        inquiry.message or '',
        '',
        f'Submitted: {inquiry.created_at}',
        f'IP:        {inquiry.ip_address or "—"}',
        '',
        'View in admin panel: /admin/inquiries/' + str(inquiry.id),
    ]
    text_body = '\n'.join(body_lines)

    html_body = f"""
    <html><body style="font-family:sans-serif;line-height:1.5;color:#111">
      <h2 style="color:#2e7d32">New inquiry — {site_name}</h2>
      <table cellpadding="6" style="border-collapse:collapse">
        <tr><td><b>Name</b></td><td>{inquiry.name}</td></tr>
        <tr><td><b>Company</b></td><td>{inquiry.company or '—'}</td></tr>
        <tr><td><b>Email</b></td><td><a href="mailto:{inquiry.email}">{inquiry.email}</a></td></tr>
        <tr><td><b>Phone</b></td><td>{inquiry.phone or '—'}</td></tr>
        <tr><td><b>Product</b></td><td>{inquiry.product_service or '—'}</td></tr>
        <tr><td><b>Quantity</b></td><td>{inquiry.quantity or '—'}</td></tr>
      </table>
      <p><b>Message:</b></p>
      <p style="white-space:pre-wrap;background:#f5f5f5;padding:12px;border-radius:6px">{inquiry.message or ''}</p>
      <p style="color:#666;font-size:13px">Submitted: {inquiry.created_at} · IP: {inquiry.ip_address or '—'}</p>
      <p><a href="{current_app.config.get('SITE_URL', '')}/admin/inquiries/{inquiry.id}">Open in admin panel</a></p>
    </body></html>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = cfg['default_sender']
    msg['To'] = to_addr
    msg['Reply-To'] = inquiry.email
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(cfg['server'], cfg['port'], timeout=20) as server:
            if cfg['use_tls']:
                server.starttls()
            if cfg['username'] and cfg['password']:
                server.login(cfg['username'], cfg['password'])
            server.sendmail(cfg['default_sender'], [to_addr], msg.as_string())
        current_app.logger.info('Inquiry notification email sent to %s', to_addr)
        return True
    except Exception as exc:
        current_app.logger.warning('Failed to send inquiry email: %s', exc)
        return False
