import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ArbitrParser:
    """Парсер для получения данных с kad.arbitr.ru"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.wait = None

    def init_driver(self):
        self.driver = Driver(
            browser="chrome", headless=self.headless, uc=True
        )
        self.wait = WebDriverWait(self.driver, 15)

    def parse(self, case_number: str) -> dict:

        result = {"success": False, "last_date": None, "document_name": None}

        try:
            logger.info(f"Начинаем парсинг дела {case_number}")
            self.init_driver()

            logger.info("Открываем kad.arbitr.ru...")
            self.driver.get("https://kad.arbitr.ru/")
            time.sleep(2)

            logger.info(f"Вводим номер дела {case_number}...")
            search_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[placeholder='например, А50-5568/08']")
                )
            )
            search_input.send_keys(case_number)
            search_input.send_keys("\n")
            time.sleep(2)

            logger.info("Кликаем по ссылке дела...")
            case_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.num_case"))
            )
            case_link.click()
            time.sleep(1)

            main_tab = self.driver.current_window_handle
            self.wait.until(lambda d: len(d.window_handles) > 1)
            for tab in self.driver.window_handles:
                if tab != main_tab:
                    self.driver.switch_to.window(tab)
                    logger.info("Переключились на новую вкладку")
                    break

            time.sleep(2)

            logger.info("Кликаем на 'Электронное дело'...")
            electronic_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(text(), 'Электронное дело')]")
                )
            )
            electronic_btn.click()
            time.sleep(2)

            logger.info("Получаем данные из таблицы...")
            date_element = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "p.b-case-chrono-ed-item-date")
                )
            )
            result["last_date"] = date_element.text.strip()
            logger.info(f"Дата: {result['last_date']}")

            content_element = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "li.b-case-chrono-ed-item")
                )
            )

            full_text = content_element.text
            result["document_name"] = full_text.split("\n")[-1].strip()
            logger.info(f"Документ: {result['document_name']}")

            result["success"] = True
            logger.info(f"Успешно получены данные по делу {case_number}")

        except Exception as e:
            logger.error(f"Ошибка при парсинге дела {case_number}: {e}")
            result["error"] = str(e)

        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Браузер закрыт")

        return result


if __name__ == "__main__":
    parser = ArbitrParser(headless=False)
    result = parser.parse("А32-28873/2024")
    print(result)
