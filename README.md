# 🍵 Matcha Stock Tracker

An automated stock monitoring tool for Marukyu Koyamaen matcha products. This Python application continuously monitors the availability of specific matcha products and sends Discord notifications when items come back in stock.

## ✨ Features

- **Automated Stock Monitoring**: Continuously checks product availability at configurable intervals
- **Discord Notifications**: Instant alerts via Discord webhook when products are in stock
- **Secure Credential Management**: Uses environment variables to keep sensitive data secure
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Multiple Detection Methods**: Uses various techniques to accurately determine stock status
- **Scheduled Monitoring**: Runs continuously with configurable check intervals

## 🛠️ Prerequisites

- Python 3.8 or higher
- A Marukyu Koyamaen account
- A Discord webhook URL
- Internet connection

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/matcha-stock-tracker.git
   cd matcha-stock-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv tracker_venv
   ```

3. **Activate the virtual environment**
   
   **Windows:**
   ```bash
   tracker_venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source tracker_venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Create a `.env` file** in the project root:
   ```bash
   # Copy the example and fill in your details
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your credentials:
   ```env
   # Marukyu Koyamaen Login Credentials
   USERNAME=your_email@example.com
   PASSWORD=your_password
   
   # Discord Webhook URL
   DISCORD_WEBHOOK=https://discord.com/api/webhooks/your_webhook_url
   
   # URLs
   LOGIN_URL=https://www.marukyu-koyamaen.co.jp/english/shop/account
   PRODUCT_URL=https://www.marukyu-koyamaen.co.jp/english/shop/products/your_product_id
   
   # Check interval in minutes
   CHECK_INTERVAL=3
   ```

### 🔧 Setting up Discord Webhook

1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Create a new webhook
4. Copy the webhook URL and paste it in your `.env` file

### 🛍️ Finding Product URLs

1. Visit [Marukyu Koyamaen English Shop](https://www.marukyu-koyamaen.co.jp/english/shop/)
2. Navigate to the product you want to monitor
3. Copy the product URL and update `PRODUCT_URL` in your `.env` file

## 🚀 Usage

### Basic Usage

Run the stock tracker:
```bash
python tracker.py
```

The application will:
- Log in to your Marukyu Koyamaen account
- Check the product availability
- Send Discord notifications if the product is in stock
- Continue monitoring at the specified interval

### Advanced Usage

You can customize the check interval by modifying `CHECK_INTERVAL` in your `.env` file:

```env
# Check every 5 minutes
CHECK_INTERVAL=5

# Check every 30 seconds (0.5 minutes)
CHECK_INTERVAL=0.5
```

## 📋 Project Structure

```
matcha-stock-tracker/
├── tracker.py          # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore rules
├── README.md          # This file
├── tracker.ipynb      # Jupyter notebook for testing
└── test.ipynb         # Additional testing notebook
```

## 🔍 How It Works

1. **Login Process**: 
   - Fetches the login page to extract CSRF tokens
   - Submits login credentials with proper form data
   - Validates login success

2. **Stock Detection**:
   - Checks for "Add to Cart" button availability
   - Looks for out-of-stock messages
   - Examines stock status classes
   - Verifies purchase form presence

3. **Notification System**:
   - Sends Discord webhook messages when stock is detected
   - Includes product URL and relevant information
   - Sends multiple notifications for visibility

## 🛡️ Security

- **Environment Variables**: All sensitive data is stored in `.env` file
- **Git Ignore**: `.env` file is excluded from version control
- **No Hardcoded Credentials**: No passwords or tokens in source code
- **Secure Sessions**: Uses proper session management for web requests

## 📝 Logging

The application provides detailed logging:
- Login attempts and results
- Stock check results
- Error messages and debugging information
- Notification delivery status

## 🐛 Troubleshooting

### Common Issues

1. **Login Failed: Invalid Email Format**
   - Check your email address in the `.env` file
   - Ensure no extra spaces or typos

2. **Import Errors**
   - Make sure you're using the virtual environment
   - Run `pip install -r requirements.txt`

3. **Discord Notifications Not Working**
   - Verify your webhook URL is correct
   - Check Discord server permissions

4. **Stock Detection Issues**
   - The website structure may have changed
   - Check the product URL is correct
   - Review logs for specific error messages

### Debug Mode

For detailed debugging, you can modify the logging level in `tracker.py`:
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Please respect the website's terms of service and rate limits. The authors are not responsible for any misuse of this software.

## 🙏 Acknowledgments

- Marukyu Koyamaen for providing quality matcha products
- The Python community for excellent libraries
- Discord for webhook functionality

---

**Happy Matcha Hunting! 🍵✨** 