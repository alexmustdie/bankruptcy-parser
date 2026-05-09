import requests

from src.config import config
from src.utils.logger import get_logger
from src.utils.retry import retry

logger = get_logger(__name__)


class FedresursParser:
    """Парсер fedresurs.ru для получения данных по ИНН"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.FEDRESURS_HEADERS)

        if config.USE_PROXY and config.PROXY_URL:
            self.session.proxies = {"http": config.PROXY_URL, "https": config.PROXY_URL}
            logger.info(
                f"Using proxy: {config.PROXY_URL.split('@')[-1]}"
            )
        else:
            logger.info("No proxy configured")

    @retry(max_retries=config.MAX_RETRIES)
    def get_person_guid(self, inn: str) -> str:
        params = {
            "searchString": inn,
            "limit": "15",
            "offset": "0",
            "isActive": "true",
        }

        response = self.session.get(
            "https://fedresurs.ru/backend/persons", params=params, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        if not data.get("pageData"):
            logger.warning(f"Person not found for INN: {inn}")
            return None

        return data["pageData"][0]["guid"]

    @retry(max_retries=config.MAX_RETRIES)
    def get_bankruptcy_info(self, guid: str) -> dict:

        response = self.session.get(
            f"https://fedresurs.ru/backend/persons/{guid}/bankruptcy", timeout=30
        )
        response.raise_for_status()

        data = response.json()
        legal_cases = data.get("legalCases", [])

        if not legal_cases:
            logger.warning(f"No bankruptcy cases found for GUID: {guid}")
            return None

        case = legal_cases[0]
        number = case.get("number")
        last_publications = case.get("lastPublications", [])

        if not last_publications:
            logger.warning(f"No publications found for case: {number}")
            return {"case_number": number, "last_date": None}

        last_date = last_publications[0].get("datePublish")
        if last_date:
            date_part = last_date.split("T")[0]
            year, month, day = date_part.split("-")
            last_date = f"{day}.{month}.{year}"

        return {"case_number": number, "last_date": last_date}

    def parse(self, inn: str) -> dict:
        logger.info(f"Parsing fedresurs for INN: {inn}")

        try:
            guid = self.get_person_guid(inn)
            if not guid:
                return {"case_number": None, "last_date": None, "success": False}

            bankruptcy_info = self.get_bankruptcy_info(guid)
            if not bankruptcy_info:
                return {"case_number": None, "last_date": None, "success": False}

            return {
                "case_number": bankruptcy_info["case_number"],
                "last_date": bankruptcy_info["last_date"],
                "success": True,
            }

        except Exception as e:
            logger.error(f"Failed to parse fedresurs for INN {inn}: {e}")
            return {"case_number": None, "last_date": None, "success": False}
