import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import requests
from src.paths import DATA_DIR


try: 
    ALPACA_API_KEY = os.environ['ALPACA_API_KEY']
    ALPACA_SECRET_KEY = os.environ['ALPACA_SECRET_KEY']
except KeyError as e:
    raise KeyError(f"Environment variable {e} not set. Please set it before running the script.")


@dataclass
class News:
    headline: str
    summary: str
    content: str
    data: datetime

def fetch_batch_of_news(
        from_date: datetime,
        to_date: datetime,
        page_token: Optional[str] = None,
) -> Tuple[list[News], str]:
    """
    Fetches a batch of news articles from Alpaca API.
    Args:
        from_date (datetime): The start date for fetching news.
        to_date (datetime): The end date for fetching news.
        page_token (str, optional): Token for pagination. Defaults to None.
    Returns:
        Tuple[list[News], str]: A tuple containing a list of News objects and the next page token.
    """
    # prepare the request URL
    headers = {
        "APCA_API_KEY_ID": ALPACA_API_KEY,
        "APCA_API_SECRET_KEY": ALPACA_SECRET_KEY,
    }
    params = {
        "start": from_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 50,
        "including_content": True,
        "sort": "ASC"
    }

    if page_token is not None:
        params["page_token"] = page_token

    url = "https://data.alpaca.markets/v1beta1/news"

    # ping Alpaca API
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch news: {e}")
    
    # parse output
    list_of_news = []
    next_page_token = None
    if response.status_code == 200: # check if the request was successful
        # parse response into json
        news_json = response.json()
        # extract next page token
        next_page_token = news_json.get("next_page_token", None)

        for item in news_json["news"]:
            # create a News object for each item in the response
            news = News(
                headline=item["headline"],
                summary=item["summary"],
                content=item["content"],
                data=datetime.fromisoformat(item["timestamp"]),
            )
            list_of_news.append(news)
    return list_of_news, next_page_token

def save_news_to_json(news_list: List[News], file_path: str) -> None:
    """
    Saves a list of News objects to a JSON file.
    Args:
        news_list (List[News]): List of News objects to save.
        file_path (str): Path to the JSON file.
    """
    news_data = [ {
        "headline": news.headline,
        "date": news.date,
        "summary": news.summary,
        "content": news.content,
        }
    for news in news_list ]
    
    # save to JSON file
    with open(file_path, "w") as f:
        json.dump(news_data, f, indent=4)

def download_historical_news(
    from_date: datetime,
    to_date: datetime,
) -> Path:
    """
    Downloads historical news from Alpaca API and stores the in a file located at
    the path returned by this function.
    """

    print(f"Downloading historical news from {from_date} to {to_date}")
    list_of_news, next_page_token = fetch_batch_of_news(from_date, to_date)
    print(f"Fetched {len(list_of_news)} news")
    print(f"Next page token: {next_page_token}")

    while next_page_token is not None:
        batch_of_news, next_page_token = fetch_batch_of_news(
            from_date, to_date, next_page_token
        )
        list_of_news += batch_of_news
        print(f"Fetched a total of {len(list_of_news)} news")
        print(f"Next page token: {next_page_token}")

        print(f"Last date in batch: {batch_of_news[-1].date}")

    # save to file
    path_to_file = (
        DATA_DIR
        / f'news_{from_date.strftime("%Y-%m-%d")}_{to_date.strftime("%Y-%m-%d")}.json'
    )
    save_news_to_json(list_of_news, path_to_file)

    print(f"News data saved to {path_to_file}")

    # return path to file
    return path_to_file