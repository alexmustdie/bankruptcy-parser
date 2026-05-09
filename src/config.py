import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/bankruptcy.db")
    INPUT_FILE = os.getenv("INPUT_FILE", "./data/inn_list.xlsx")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))
    MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "3"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    PROXY_URL = os.getenv("PROXY_URL")
    USE_PROXY = (
        os.getenv("USE_PROXY", "false").lower() == "true"
    )

    FEDRESURS_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://fedresurs.ru/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    ARBITR_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://kad.arbitr.ru",
        "Referer": "https://kad.arbitr.ru/",
    }


config = Config()
