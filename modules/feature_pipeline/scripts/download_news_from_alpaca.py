from datetime import datetime
import sys
import os

# # Add the correct path to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.alpaca_news_api import download_historical_news

download_historical_news(
    from_date=datetime(2025, 4, 20),
    to_date=datetime.now(),
)