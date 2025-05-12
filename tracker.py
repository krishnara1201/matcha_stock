import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

LOGIN_URL = "https://www.marukyu-koyamaen.co.jp/english/shop/account"
PRODUCT_URL = "https://www.marukyu-koyamaen.co.jp/english/shop/products/11b1100c1"
USERNAME = "17aayushisharma@gmail.com"
PASSWORD = "Wishiandputta25"

# Create session to persist cookies
session = requests.Session()

# Check interval (in minutes)
CHECK_INTERVAL = 3

# 1. Log in
login_data = {
    "username": USERNAME,
    "password": PASSWORD,
    # Add hidden form fields (check page source)
    "csrf_token": "extract_from_login_page" 
}

login_response = session.post(LOGIN_URL, data=login_data)
login_response.raise_for_status()  # Check login success

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1369816851621613661/Xz73QCKu_YaxoRSrKRLngfwanWoH-OYzdnu6XJjdgSmKTFGqx9JKL7II0sYMWCPbYLlH"


def login_and_check_stock():
    session = requests.Session()
    
    try:
        # Step 1: Get the login page to extract any CSRF token if needed
        login_page = session.get(LOGIN_URL)
        
        # You may need to extract CSRF token - modify as needed
        # csrf_token = login_soup.find('input', {'name': 'csrf_token'}).get('value')
        
        # Step 2: Submit login form
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "csrf_token": "extract_from_login_page"  # Uncomment if needed
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        
        if login_response.status_code != 200:
            logger.error(f"Login failed with status code: {login_response.status_code}")
            return
            
        logger.info("Login successful")
        
        # Step 3: Check the product page
        product_page = session.get(PRODUCT_URL)
        product_soup = BeautifulSoup(product_page.text, 'html.parser')
        
        # Check for in-stock status using the classes you provided
        in_stock_element = product_soup.find(class_="product product-type-variable status-publish instock")
        out_of_stock_element = product_soup.find(class_="product product-type-variable status-publish outofstock")
        
        if in_stock_element or len(out_of_stock_element) != 2:
            logger.info("Product is IN STOCK! 🎉")
            for i in range(10):
                send_notification("Product is IN STOCK! 🎉 Go to: " + PRODUCT_URL)
                time.sleep(1)  # Sleep for 1 second between notifications
            return True
        elif out_of_stock_element:
            logger.info("Product is still out of stock")
            return False
        else:
            logger.warning("Could not determine stock status")
            return None
            
    except Exception as e:
        logger.error(f"Error checking stock: {str(e)}")
        return None
    
def send_notification(message):
# Send Discord notification
    if DISCORD_WEBHOOK:
        try:
            discord_data = {"content": message}
            requests.post(DISCORD_WEBHOOK, json=discord_data)
            logger.info("Discord notification sent")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {str(e)}")


if __name__ == "__main__":
    logger.info(f"Stock checker started. Checking every {CHECK_INTERVAL} minutes.")
    
    # Run once immediately
    login_and_check_stock()
    
    # Then schedule regular checks
    scheduler = BlockingScheduler()
    scheduler.add_job(login_and_check_stock, 'interval', minutes=CHECK_INTERVAL)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stock checker stopped")