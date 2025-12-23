import httpx
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    def trigger_webhook(self, url: str, payload: dict):
        """
        Triggers an external webhook (e.g. n8n) with the submission payload.
        Synchronous version for MVP compativility with threads.
        """
        if not url:
            return

        try:
            # Short timeout to not block thread too long
            with httpx.Client(timeout=5.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"Webhook {url} success: {response.status_code}")
        except Exception as e:
            logger.error(f"Webhook {url} failed: {str(e)}")

webhook_service = WebhookService()
