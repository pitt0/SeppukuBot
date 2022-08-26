import praw
import os

from dotenv import load_dotenv

load_dotenv('secrets/.env')

reddit = praw.Reddit(
    client_id=os.getenv('CLIENT_ID'), # type: ignore[valid-type]
    client_secret=os.getenv('SECRET'), # type: ignore[valid-type]
    user_agent='SeppukuBot',
    check_for_async=False,
)