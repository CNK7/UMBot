import os
from dotenv import load_dotenv

load_dotenv()

# Telegram 配置
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# BEpusdt 配置
BEPUSDT_API_URL = os.getenv('BEPUSDT_API_URL')
BEPUSDT_APP_ID = os.getenv('BEPUSDT_APP_ID')
BEPUSDT_APP_SECRET = os.getenv('BEPUSDT_APP_SECRET')
BEPUSDT_NOTIFY_URL = os.getenv('BEPUSDT_NOTIFY_URL')

# Blockchain Network Configuration
NETWORK_PROVIDER = os.getenv('NETWORK_PROVIDER', 'https://api.trongrid.io')

# USDT Contract Address (TRC20)
USDT_CONTRACT_ADDRESS = os.getenv('USDT_CONTRACT_ADDRESS')

# Store Configuration
STORE_NAME = "UMBot Store"
STORE_DESCRIPTION = "Your one-stop shop for digital goods"

# Payment Configuration
PAYMENT_TIMEOUT = 30  # minutes
CONFIRMATION_BLOCKS = 12  # number of blocks to wait for confirmation

# Database Configuration (if needed)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///store.db')