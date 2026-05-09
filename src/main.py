import time
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import config
from src.database import db
from src.models import ArbitrData, FedresursData
from src.parsers.arbitr_parser import ArbitrParser
from src.parsers.fedresurs_parser import FedresursParser
from src.utils.excel_reader import read_inn_from_excel
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BankruptcyParser:
    def __init__(self):
        self.fedresurs_parser = FedresursParser()
        self.arbitr_parser = ArbitrParser(headless=True)
        self.processed_inns = db.get_processed_inns()

    def process_single_inn(self, inn: str) -> dict:
        result = {
            "inn": inn,
            "case_number": None,
            "fedresurs_last_date": None,
            "arbitr_last_date": None,
            "document_name": None,
            "success": False,
        }

        try:
            logger.info(f"Парсинг fedresurs для ИНН: {inn}")
            fedresurs_data = self.fedresurs_parser.parse(inn)

            if not fedresurs_data["success"] or not fedresurs_data["case_number"]:
                logger.warning(f"Не найдено дело о банкротстве для ИНН: {inn}")
                return result

            result["case_number"] = fedresurs_data["case_number"]
            result["fedresurs_last_date"] = fedresurs_data["last_date"]

            with db.get_session() as session:
                existing = (
                    session.query(FedresursData)
                    .filter(FedresursData.inn == inn)
                    .first()
                )

                if existing:
                    existing.case_number = result["case_number"]
                    existing.last_date = db.parse_date(result["fedresurs_last_date"])
                    fedresurs_id = existing.id
                    logger.info(f"Updated fedresurs data for INN: {inn}")
                else:
                    new_data = FedresursData(
                        inn=inn,
                        case_number=result["case_number"],
                        last_date=db.parse_date(result["fedresurs_last_date"]),
                    )
                    session.add(new_data)
                    session.flush()
                    fedresurs_id = new_data.id
                    logger.info(f"Saved fedresurs data for INN: {inn}")

            logger.info(
                f"Получен номер дела: {result['case_number']}, fedresurs_id={fedresurs_id}"
            )

            logger.info(f"Парсинг arbitr для дела: {result['case_number']}")
            arbitr_data = self.arbitr_parser.parse(result["case_number"])

            if arbitr_data["success"]:
                result["arbitr_last_date"] = arbitr_data["last_date"]
                result["document_name"] = arbitr_data["document_name"]

                with db.get_session() as session:
                    existing = (
                        session.query(ArbitrData)
                        .filter(ArbitrData.case_number == result["case_number"])
                        .first()
                    )

                    if existing:
                        existing.last_date = db.parse_date(result["arbitr_last_date"])
                        existing.document_name = result["document_name"]
                        existing.fedresurs_id = fedresurs_id
                        logger.info(
                            f"Updated arbitr data for case: {result['case_number']}"
                        )
                    else:
                        new_data = ArbitrData(
                            case_number=result["case_number"],
                            last_date=db.parse_date(result["arbitr_last_date"]),
                            document_name=result["document_name"],
                            fedresurs_id=fedresurs_id,
                        )
                        session.add(new_data)
                        logger.info(
                            f"Saved arbitr data for case: {result['case_number']}"
                        )

                logger.info(
                    f"Получены данные из arbitr: дата={result['arbitr_last_date']}, документ={result['document_name']}"
                )

            result["success"] = True

            time.sleep(config.REQUEST_DELAY)

        except Exception as e:
            logger.error(f"Ошибка при обработке ИНН {inn}: {e}")

        return result

    def run(self, input_file: str):

        logger.info("Starting bankruptcy parser")

        try:
            inns = read_inn_from_excel(input_file)
        except Exception as e:
            logger.error(f"Failed to read input file: {e}")
            return

        pending_inns = [inn for inn in inns if inn not in self.processed_inns]
        logger.info(
            f"Total INNs: {len(inns)}, already processed: {len(self.processed_inns)}, pending: {len(pending_inns)}"
        )

        if not pending_inns:
            logger.info("All INNs already processed")
            return

        results = []
        with ThreadPoolExecutor(max_workers=config.MAX_CONCURRENT) as executor:
            futures = {
                executor.submit(self.process_single_inn, inn): inn
                for inn in pending_inns
            }

            for future in as_completed(futures):
                inn = futures[future]
                try:
                    result = future.result()
                    results.append(result)

                    if result["success"]:
                        logger.info(
                            f"Successfully processed INN: {inn} -> case: {result['case_number']}"
                        )
                    else:
                        logger.warning(f"Failed to process INN: {inn}")

                except Exception as e:
                    logger.error(f"Unexpected error for INN {inn}: {e}")

        successful = sum(1 for r in results if r["success"])
        logger.info(
            f"Processing completed. Successful: {successful}/{len(pending_inns)}"
        )


def main():
    parser = argparse.ArgumentParser(description="Bankruptcy data parser")
    parser.add_argument(
        "--file",
        type=str,
        default=config.INPUT_FILE,
        help="Path to Excel file with INNs",
    )
    args = parser.parse_args()

    app = BankruptcyParser()
    app.run(args.file)


if __name__ == "__main__":
    main()
