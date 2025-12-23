from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class PaymentIntentRequest(BaseModel):
    amount: int  # Amount in cents
    currency: str = "usd"
    description: str = "Form submission payment"

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str

@router.post("/create-intent", response_model=PaymentIntentResponse)
def create_payment_intent(request: PaymentIntentRequest):
    """
    Create a Stripe PaymentIntent for frontend to complete.
    """
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured. Add STRIPE_SECRET_KEY to .env"
        )
    
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            automatic_payment_methods={"enabled": True},
        )
        
        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            payment_intent_id=intent.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
