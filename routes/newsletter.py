from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, NewsletterSubscription

newsletter_bp = Blueprint('newsletter', __name__, url_prefix='/newsletter')

@newsletter_bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    subscription = NewsletterSubscription.query.filter_by(user_id=current_user.id).first()
    if subscription and subscription.is_active:
        flash('You are already subscribed', 'info')
    else:
        if subscription:
            subscription.is_active = True
        else:
            subscription = NewsletterSubscription(user_id=current_user.id, is_active=True)
            db.session.add(subscription)
        db.session.commit()
        flash('Successfully subscribed!', 'success')

    return redirect(request.referrer or url_for('main.index'))

@newsletter_bp.route('/unsubscribe', methods=['POST'])
@login_required
def unsubscribe():
    subscription = NewsletterSubscription.query.filter_by(user_id=current_user.id).first()

    if subscription:
        subscription.is_active = False
        db.session.commit()
        flash('You have been unsubscribed', 'success')

    return redirect(request.referrer or url_for('main.index'))
