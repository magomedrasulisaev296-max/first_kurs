import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Callable

import pandas as pd

log_dir = Path("logs_output")
log_dir.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_file = log_dir / f"{__name__}.log"
file_handler = logging.FileHandler(log_file)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)


def read_excel_file(road_to_excel_file: str):
    """возврощает excel файлы в ввиде словоря"""
    return pd.read_excel(road_to_excel_file)


df = read_excel_file("../data/operations.xlsx")


def report_to_file(filename: str | None = None) -> Callable:
    logger.info("Начата обработка функции")
    """
    записывает вывод функции в json файл

    filename: авто имя или заданное пользователем
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            file_name = filename or f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("reports", exist_ok=True)
            file_path = os.path.join("reports", file_name)

            if isinstance(result, pd.DataFrame):
                logger.info("входные данные прошли проверку работа продолжается")
                needed_columns = ["Дата платежа", "Категория", "Сумма платежа"]
                result_filtered = result[needed_columns].copy()
                result_filtered["Дата платежа"] = result_filtered["Дата платежа"].dt.strftime("%d.%m.%Y")
                total_sum = float(abs(result_filtered["Сумма платежа"].sum())) if not result_filtered.empty else 0.0
                json_data = {
                    "total_sum": total_sum,
                    "transactions": result_filtered.to_dict("records"),
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                    logger.info("отчет составлен и будет сохранен в виде отдельного файла")
            print(f"📄 Отчет сохранен: {file_path}")
            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(df_, category, date):
    """выводит траты по категории и заданной дате на три месяца назад"""
    df = df_.copy()
    day, month, year = date
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y", dayfirst=True, errors="coerce")
    end_date = datetime(year, month, day)
    start_date = end_date - timedelta(days=90)
    mask = (
        (df["Категория"] == category)
        & (df["Дата платежа"] >= start_date)
        & (df["Дата платежа"] <= end_date)
        & (df["Сумма платежа"] < 0)
    )
    result = df[mask].sort_values("Дата платежа", ascending=False)
    if len(result) > 0:
        total_spent = abs(result["Сумма платежа"].sum())  # модуль суммы
        result["Итог"] = f"Всего потрачено: {total_spent:.2f} руб"

    return result
