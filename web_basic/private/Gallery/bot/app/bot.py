from quart import Quart, request
from playwright.async_api import async_playwright
import os, asyncio, logging

FLAG = os.environ.get('FLAG', 'flag{G4ll3ry_XSS_M4st3r_2024}')

app = Quart(__name__)
app.secret_key = os.urandom(32)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def admin_visit(url):
    """
    Admin bot that visits reported URLs
    """
    success = True
    
    try:
        logger.info(f"Starting admin visit to: {url}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch_persistent_context(
            user_data_dir='/tmp/admin_browser',
            headless=True,
            args=[
                "--window-size=1920x1080",
                "--disable-gpu", 
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        )

        page = await browser.new_page()
        
        # Set admin cookies with flag
        await page.context.add_cookies([
            {
                "name": "admin_session",
                "value": "admin_authenticated_session_12345",
                "domain": "web",
                "path": "/"
            },
            {
                "name": "flag",
                "value": FLAG,
                "domain": "web", 
                "path": "/"
            },
            {
                "name": "user_role",
                "value": "administrator", 
                "domain": "web",
                "path": "/"
            }
        ])
        
        # Visit the main site first to establish session
        logger.info("Visiting main gallery page...")
        await page.goto("http://web/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        
        # Visit admin panel to check for any alerts/XSS
        logger.info("Visiting admin panel...")
        await page.goto("http://web/admin", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)
        
        # Now visit the reported URL
        logger.info(f"Visiting reported URL: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Stay on page for a while to let any XSS execute
        await asyncio.sleep(5)
        
        # Interact with the page (scroll, click elements)
        try:
            # Scroll to make sure all content loads
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # If it's an image detail page, try to like and comment
            if "/image/" in url:
                logger.info("Detected image page, interacting...")
                
                # Try to like the image
                like_button = page.locator("button:has-text('Like')")
                if await like_button.count() > 0:
                    await like_button.click()
                    await asyncio.sleep(1)
                
                # Try to add a comment
                comment_input = page.locator("textarea[name='comment']")
                if await comment_input.count() > 0:
                    await comment_input.fill("Nice artwork! - Admin Review")
                    
                    submit_button = page.locator("button[type='submit']:has-text('Post')")
                    if await submit_button.count() > 0:
                        await submit_button.click()
                        await asyncio.sleep(2)
            
            # If it's the admin panel, interact with it
            elif "/admin" in url:
                logger.info("Detected admin panel, performing admin tasks...")
                
                # Click refresh button if available
                refresh_button = page.locator("button:has-text('Refresh')")
                if await refresh_button.count() > 0:
                    await refresh_button.click()
                    await asyncio.sleep(2)
                
                # Check view buttons
                view_buttons = page.locator("button:has-text('View')")
                count = await view_buttons.count()
                if count > 0:
                    # Click first view button
                    await view_buttons.first.click()
                    await asyncio.sleep(2)
            
        except Exception as e:
            logger.warning(f"Error during page interaction: {e}")
        
        # Final wait to ensure any delayed XSS executes
        await asyncio.sleep(3)
        
        logger.info("Admin visit completed successfully")
        
    except Exception as e:
        logger.error(f"Error during admin visit: {e}")
        success = False
    finally:
        try:
            await browser.close()
            await playwright.stop()
        except:
            pass
        
        # Clean up browser data
        try:
            os.system('rm -rf /tmp/admin_browser')
        except:
            pass
            
    return success

@app.route('/report', methods=['POST'])
async def handle_report():
    """
    Handle incoming reports and trigger admin visit
    """
    try:
        form = await request.get_json()
        url = form.get('url', '').strip()
        reason = form.get('reason', 'No reason provided')
        
        if not url:
            logger.warning("Report received with no URL")
            return "URL is required", 400
        
        logger.info(f"Report received - URL: {url}, Reason: {reason}")
        
        # Validate URL format (basic security)
        if not url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid URL format: {url}")
            return "Invalid URL format", 400
        
        # Allow internal and external URLs for testing
        allowed_hosts = ['web', 'localhost', '127.0.0.1', 'webhook.site']
        url_host = url.split('//')[1].split('/')[0].split(':')[0]
        
        if not any(host in url_host for host in allowed_hosts):
            logger.warning(f"Blocked external URL: {url}")
            return "External URLs not allowed", 400
        
        # Schedule admin visit
        logger.info(f"Scheduling admin visit to: {url}")
        success = await admin_visit(url)
        
        if success:
            logger.info("Admin successfully reviewed the reported content")
            return "Admin will review the reported content", 200
        else:
            logger.error("Admin failed to review the content") 
            return "Failed to schedule review", 500
            
    except Exception as e:
        logger.error(f"Error handling report: {e}")
        return "Internal server error", 500

@app.route('/health')
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "gallery-admin-bot"}, 200

if __name__ == '__main__':
    logger.info("Starting Gallery Admin Bot...")
    app.run('0.0.0.0', 80, debug=False)
