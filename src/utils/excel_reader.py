import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


def read_inn_from_excel(file_path: str, column_name: str = "ИНН") -> list:

    try:
        df = pd.read_excel(file_path)
        if column_name not in df.columns:
            for col in df.columns:
                if "инн" in col.lower():
                    column_name = col
                    break
            else:
                raise ValueError(f"Column '{column_name}' not found in Excel file")

        inns = df[column_name].astype(str).str.strip().tolist()
        inns = [inn for inn in inns if inn and inn != "nan"]

        logger.info(f"Loaded {len(inns)} INNs from {file_path}")
        return inns

    except Exception as e:
        logger.error(f"Failed to read Excel file: {e}")
        raise
