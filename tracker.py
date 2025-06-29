import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import logging
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Get configuration from environment variables
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
LOGIN_URL = os.getenv('LOGIN_URL')
PRODUCT_URL = os.getenv('PRODUCT_URL')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 3))

# Validate required environment variables
if not all([USERNAME, PASSWORD, DISCORD_WEBHOOK, LOGIN_URL, PRODUCT_URL]):
    logger.error("Missing required environment variables. Please check your .env file.")
    exit(1)

def extract_csrf_token(soup):
    """Extract CSRF token from login page"""
    csrf_input = soup.find('input', {'name': 'woocommerce-login-nonce'})
    if csrf_input:
        return csrf_input.get('value')
    
    # Try alternative CSRF token names
    for token_name in ['_wpnonce', 'security', 'nonce']:
        csrf_input = soup.find('input', {'name': token_name})
        if csrf_input:
            return csrf_input.get('value')
    
    return None

def login_to_website():
    """Login to the Marukyu Koyamaen website"""
    session = requests.Session()
    
    try:
        # Step 1: Get the login page to extract CSRF token
        logger.info("Getting login page...")
        login_page_response = session.get(LOGIN_URL)
        login_page_response.raise_for_status()
        
        login_soup = BeautifulSoup(login_page_response.text, 'html.parser')
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(login_soup)
        if csrf_token:
            logger.info("CSRF token found")
        else:
            logger.warning("No CSRF token found, proceeding without it")
        
        # Step 2: Submit login form
        login_data = {
            'username': USERNAME,
            'password': PASSWORD,
            'login': 'Log in'
        }
        
        if csrf_token:
            login_data['woocommerce-login-nonce'] = csrf_token
        
        logger.info("Attempting login...")
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        # Check if login was successful
        if login_response.status_code == 200:
            # Check if we're redirected to a different page (successful login)
            if 'my-account' in login_response.url or 'dashboard' in login_response.url:
                logger.info("Login successful!")
                return session
            else:
                # Check if there are error messages on the page
                login_soup = BeautifulSoup(login_response.text, 'html.parser')
                error_messages = login_soup.find_all(class_='woocommerce-error')
                if error_messages:
                    logger.error(f"Login failed: {error_messages[0].get_text().strip()}")
                    return None
                else:
                    logger.info("Login appears successful")
                    return session
        else:
            logger.error(f"Login failed with status code: {login_response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return None

def check_stock_status(session):
    """Check the stock status of the product"""
    try:
        logger.info("Checking product page...")
        product_response = session.get(PRODUCT_URL)
        product_response.raise_for_status()
        
        product_soup = BeautifulSoup(product_response.text, 'html.parser')
        
        # Multiple methods to detect stock status
        stock_status = None
        
        # Method 1: Check for "Add to Cart" button
        add_to_cart_button = product_soup.find('button', {'name': 'add-to-cart'})
        if add_to_cart_button and not add_to_cart_button.get('disabled'):
            stock_status = 'in_stock'
            logger.info("Product appears to be in stock (Add to Cart button available)")
        
        # Method 2: Check for out of stock messages
        out_of_stock_messages = product_soup.find_all(text=re.compile(r'out of stock|sold out|unavailable', re.IGNORECASE))
        if out_of_stock_messages:
            stock_status = 'out_of_stock'
            logger.info("Product appears to be out of stock")
        
        # Method 3: Check for stock status classes
        stock_elements = product_soup.find_all(class_=re.compile(r'stock|availability'))
        for element in stock_elements:
            element_text = element.get_text().lower()
            if 'in stock' in element_text or 'available' in element_text:
                stock_status = 'in_stock'
                logger.info("Product appears to be in stock")
                break
            elif 'out of stock' in element_text or 'unavailable' in element_text:
                stock_status = 'out_of_stock'
                logger.info("Product appears to be out of stock")
                break
        
        # Method 4: Check for form availability
        if not stock_status:
            # Look for purchase form
            purchase_form = product_soup.find('form', {'class': 'cart'})
            if purchase_form:
                stock_status = 'in_stock'
                logger.info("Product appears to be in stock (purchase form available)")
            else:
                stock_status = 'out_of_stock'
                logger.info("Product appears to be out of stock (no purchase form)")
        
        return stock_status
        
    except Exception as e:
        logger.error(f"Error checking stock status: {str(e)}")
        return None

def send_notification(message):
    """Send Discord notification"""
    if DISCORD_WEBHOOK:
        try:
            discord_data = {"content": message}
            response = requests.post(DISCORD_WEBHOOK, json=discord_data)
            response.raise_for_status()
            logger.info("Discord notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {str(e)}")

def check_stock_and_notify():
    """Main function to check stock and send notifications"""
    logger.info("Starting stock check...")
    
    # Login to the website
    session = login_to_website()
    if not session:
        logger.error("Failed to login, skipping stock check")
        return False
    
    # Check stock status
    stock_status = check_stock_status(session)
    
    if stock_status == 'in_stock':
        logger.info("🎉 PRODUCT IS IN STOCK! 🎉")
        message = f"🎉 **MATCHA IS IN STOCK!** 🎉\n\nProduct: Marukyu Koyamaen Matcha\nURL: {PRODUCT_URL}\n\nHurry up and order now!"
        
        # Send multiple notifications
        for i in range(5):
            send_notification(message)
            time.sleep(1)
        
        return True
    elif stock_status == 'out_of_stock':
        logger.info("Product is still out of stock")
        return False
    else:
        logger.warning("Could not determine stock status")
        return False

def main():
    """Main function to run the stock checker"""
    logger.info(f"Stock checker started. Checking every {CHECK_INTERVAL} minutes.")
    logger.info(f"Monitoring: {PRODUCT_URL}")
    
    # Run once immediately
    check_stock_and_notify()
    
    # Then schedule regular checks
    scheduler = BlockingScheduler()
    scheduler.add_job(check_stock_and_notify, 'interval', minutes=CHECK_INTERVAL)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stock checker stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()