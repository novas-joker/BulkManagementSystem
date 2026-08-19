"""
Engagement tracking routes for email open/click tracking and unsubscribe handling.
Provides endpoints for:
- Open pixel tracking (1x1 transparent pixel)
- Click link tracking (302 redirect)
- One-click unsubscribe (RFC 8058 compliant)
"""
import logging
from fastapi import APIRouter, Query, HTTPException, status, Request
from fastapi.responses import Response, RedirectResponse

from app.tasks.events import log_email_open_task, log_email_click_task, log_unsubscribe_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/track", tags=["Engagement Tracking"])


@router.get("/open/{token}", response_class=Response)
async def track_email_open(
    token: str,
    request: Request,
):
    """
    Email open tracking endpoint (1x1 transparent pixel).
    
    Returns a 1x1 transparent GIF pixel. When an email containing this URL
    is opened, the pixel is fetched, recording the open event.
    
    Args:
        token: Secure tracking token (from campaign recipient)
        
    Returns:
        1x1 transparent GIF image
    """
    # Note: db and request are injected via FastAPI
    # Get request and db from context if available
    
    try:
        # Extract user agent and IP
        user_agent = request.headers.get("User-Agent", "") if request else ""
        ip_address = request.client.host if request else ""
        
        # Decrypt and verify token here (implementation depends on token format)
        # For now, we assume token is campaign_recipient_id
        campaign_recipient_id = token
        
        # Dispatch async task to log open
        log_email_open_task.delay(campaign_recipient_id, user_agent, ip_address)
        
        logger.info(f"Open tracked for {campaign_recipient_id}")
        
    except Exception as exc:
        logger.exception(f"Error tracking open for token {token}: {exc}")
    
    # Return 1x1 transparent GIF regardless of success
    # This ensures the pixel loads and pixel blocking doesn't prevent tracking
    gif = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
        b"\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01"
        b"\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02"
        b"\x44\x01\x00\x3b"
    )
    return Response(content=gif, media_type="image/gif", status_code=200)


@router.get("/click/{token}")
async def track_click_and_redirect(
    token: str,
    request: Request,
    url: str = Query(...),
):
    """
    Email click tracking endpoint with redirect.
    
    Logs a click event and then redirects to the original URL.
    Uses 302 Found status for temporary redirects.
    
    Args:
        token: Secure tracking token (from campaign recipient)
        url: Target URL to redirect to (URL-encoded)
        
    Returns:
        302 redirect to the original URL
    """
    try:
        # Extract user agent and IP
        user_agent = request.headers.get("User-Agent", "") if request else ""
        ip_address = request.client.host if request else ""
        
        # Decrypt and verify token here (implementation depends on token format)
        campaign_recipient_id = token
        
        # Dispatch async task to log click
        log_email_click_task.delay(campaign_recipient_id, url, user_agent, ip_address)
        
        logger.info(f"Click tracked for {campaign_recipient_id} on {url}")
        
    except Exception as exc:
        logger.exception(f"Error tracking click for token {token}: {exc}")
    
    # Redirect to the original URL regardless of success
    # This ensures user experience isn't affected by tracking
    return RedirectResponse(url=url, status_code=302)


@router.post("/unsubscribe/{token}")
async def unsubscribe_one_click(
    token: str,
    reason: str = Query(default="", description="Optional reason for unsubscribe"),
):
    """
    One-click unsubscribe endpoint (RFC 8058 compliant).
    
    Handles one-click unsubscribe requests from email clients.
    Immediately removes the contact from the campaign mailing.
    
    Args:
        token: Secure tracking token (from campaign recipient)
        reason: Optional reason for unsubscribe
        
    Returns:
        200 OK with confirmation message
    """
    try:
        # Decrypt and verify token here (implementation depends on token format)
        campaign_recipient_id = token
        
        # Dispatch async task to log unsubscribe
        log_unsubscribe_task.delay(campaign_recipient_id, reason)
        
        logger.info(f"Unsubscribe requested for {campaign_recipient_id}, reason: {reason}")
        
        return {
            "status": "success",
            "message": "You have been unsubscribed from this mailing list.",
            "timestamp": "2026-08-17T00:00:00Z",
        }
        
    except Exception as exc:
        logger.exception(f"Error processing unsubscribe for token {token}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process unsubscribe request",
        )


@router.get("/unsubscribe/{token}", response_class=Response)
async def unsubscribe_web_page(
    token: str,
):
    """
    Web-based unsubscribe page.
    
    Provides an HTML page for web-based unsubscribe (fallback from email).
    Can include preference management if needed in future.
    
    Args:
        token: Secure tracking token (from campaign recipient)
        
    Returns:
        HTML page confirming unsubscribe
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unsubscribe</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; }
            .container { max-width: 600px; margin: 50px auto; text-align: center; }
            h1 { color: #333; }
            p { color: #666; }
            .button { background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Manage Your Subscription</h1>
            <p>Click below to unsubscribe from our mailing list.</p>
            <form method="POST" action="/track/unsubscribe/{token}">
                <button type="submit" class="button">Confirm Unsubscribe</button>
            </form>
            <p><small>You will not receive further emails from us.</small></p>
        </div>
    </body>
    </html>
    """.format(token=token)
    
    return Response(content=html_content, media_type="text/html", status_code=200)
