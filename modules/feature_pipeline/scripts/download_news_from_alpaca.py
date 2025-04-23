from datetime import datetime
from src.alpaca_news_api import download_historical_news


download_historical_news(
    from_date=datetime(2025, 4, 20),
    to_date=datetime.now(),
)