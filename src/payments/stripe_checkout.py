"""
Stripe Integration for FareGlitch

Two flows:
A) SUBSCRIPTION: $5/month → unlimited SMS deal alerts
   1. User enters email + phone on fareglitch.com.au
   2. We create a Stripe Checkout Session (subscription mode)
   3. User pays → Stripe webhook → we activate their subscription
   4. They get SMS alerts for every deal, 1 hour before Instagram

B) REFUND: Glitch Guarantee
   - If an airline cancels the fare within 48h, subscriber can request refund
"""
import logging
import time
from typing import Optional

import stripe

from src.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


# ------------------------------------------------------------------
# Subscription flow ($5/month)
# ------------------------------------------------------------------

def create_subscription_checkout(
    email: str,
    phone: str,
    success_url: str = None,
    cancel_url: str = None,
) -> dict:
    """
    Create a Stripe Checkout Session for $5/month subscription.

    Returns:
        {"checkout_url": "https://checkout.stripe.com/...", "session_id": "cs_..."}
    """
    if not settings.stripe_secret_key:
        raise ValueError("STRIPE_SECRET_KEY not configured")

    base_url = "https://fareglitch.com.au"
    success_url = success_url or f"{base_url}/home?subscribed=true"
    cancel_url = cancel_url or f"{base_url}/home?cancelled=true"

    # Use existing Stripe Price ID if set, otherwise create price inline
    if settings.stripe_price_id:
        line_items = [{"price": settings.stripe_price_id, "quantity": 1}]
    else:
        line_items = [
            {
                "price_data": {
                    "currency": settings.stripe_currency,
                    "unit_amount": int(settings.subscription_price_aud * 100),
                    "recurring": {"interval": "month"},
                    "product_data": {
                        "name": "FareGlitch Premium",
                        "description": (
                            "Unlimited SMS deal alerts, 1 hour before Instagram. "
                            "Cancel anytime."
                        ),
                    },
                },
                "quantity": 1,
            }
        ]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        customer_email=email,
        line_items=line_items,
        metadata={
            "phone": phone,
            "email": email,
            "type": "subscription",
        },
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={
            "metadata": {
                "phone": phone,
                "email": email,
            },
        },
        allow_promotion_codes=True,
    )

    logger.info(f"💳 Subscription checkout: {email} ({phone})")

    return {
        "checkout_url": session.url,
        "session_id": session.id,
    }


# ------------------------------------------------------------------
# One-off deal unlock (legacy / fallback)
# ------------------------------------------------------------------

def create_checkout_session(
    deal_number: str,
    deal_headline: str,
    amount_aud: float,
    customer_email: str,
    success_url: str = None,
    cancel_url: str = None,
) -> dict:
    """
    Create a Stripe Checkout Session for unlocking a single deal.
    (Kept for backwards compatibility, but subscriptions are primary.)
    """
    if not settings.stripe_secret_key:
        raise ValueError("STRIPE_SECRET_KEY not configured")

    base_url = "https://api.fareglitch.com.au"
    success_url = success_url or f"{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = cancel_url or f"{base_url}/payment/cancelled"

    amount_cents = int(amount_aud * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=customer_email,
        line_items=[
            {
                "price_data": {
                    "currency": settings.stripe_currency,
                    "unit_amount": amount_cents,
                    "product_data": {
                        "name": f"FareGlitch Deal Unlock: {deal_number}",
                        "description": deal_headline[:200],
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={
            "deal_number": deal_number,
            "customer_email": customer_email,
            "type": "deal_unlock",
        },
        success_url=success_url,
        cancel_url=cancel_url,
        expires_at=int(time.time()) + 1800,
    )

    logger.info(f"💳 Deal checkout: {deal_number} for {customer_email} (${amount_aud} AUD)")

    return {
        "checkout_url": session.url,
        "session_id": session.id,
    }


# ------------------------------------------------------------------
# Webhook processing
# ------------------------------------------------------------------

def process_webhook_event(payload: bytes, sig_header: str) -> Optional[dict]:
    """Verify and process a Stripe webhook event."""
    if not settings.stripe_webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        logger.error("⚠️ Stripe webhook signature verification failed")
        return None
    except ValueError:
        logger.error("⚠️ Invalid Stripe webhook payload")
        return None

    return event


# ------------------------------------------------------------------
# Refunds
# ------------------------------------------------------------------

def issue_refund(payment_intent_id: str, reason: str = "requested_by_customer") -> dict:
    """Issue a full refund via Stripe (Glitch Guarantee)."""
    if not settings.stripe_secret_key:
        raise ValueError("STRIPE_SECRET_KEY not configured")

    refund = stripe.Refund.create(
        payment_intent=payment_intent_id,
        reason=reason,
    )

    logger.info(f"💸 Refund issued: {refund.id} for {payment_intent_id} ({refund.status})")

    return {
        "refund_id": refund.id,
        "status": refund.status,
        "amount": refund.amount / 100,
    }


# ------------------------------------------------------------------
# Subscription management
# ------------------------------------------------------------------

def cancel_subscription(stripe_subscription_id: str) -> dict:
    """Cancel a subscription at period end (user keeps access until paid period ends)."""
    sub = stripe.Subscription.modify(
        stripe_subscription_id,
        cancel_at_period_end=True,
    )
    logger.info(f"🚫 Subscription {stripe_subscription_id} set to cancel at period end")
    return {
        "status": "cancelling",
        "cancel_at": sub.current_period_end,
    }


def get_session_details(session_id: str) -> Optional[dict]:
    """Retrieve checkout session details."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "session_id": session.id,
            "payment_status": session.payment_status,
            "payment_intent": session.payment_intent,
            "customer_email": session.customer_email,
            "deal_number": session.metadata.get("deal_number"),
            "amount": session.amount_total / 100 if session.amount_total else 0,
        }
    except Exception as e:
        logger.error(f"Failed to retrieve session {session_id}: {e}")
        return None
