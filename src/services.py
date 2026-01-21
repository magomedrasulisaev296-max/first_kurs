# services.py (исправленная версия)
import json
import logging
from typing import Dict, List

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cashback_analysis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def analyze_cashback_categories(data: List[Dict], year: int, month: int) -> str:
    try:
        logger.info(f"Начало анализа кешбэка за {month}/{year}")

        # Если данные пустые - сразу возвращаем пустой JSON
        if not data:
            logger.warning("Получены пустые данные")
            return json.dumps({}, ensure_ascii=False)

        df = pd.DataFrame(data)

        required_columns = ["Дата операции", "Категория", "Сумма операции"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Отсутствует обязательная колонка: {col}")

        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
        mask = (df["Дата операции"].dt.year == year) & (
            df["Дата операции"].dt.month == month
        )
        monthly_data = df[mask]

        monthly_data = monthly_data[
            (monthly_data["Сумма операции"] < 0) & (monthly_data["Категория"].notna())
        ].copy()

        if monthly_data.empty:
            logger.warning(f"Нет данных за {month}/{year}")
            return json.dumps({}, ensure_ascii=False)

        category_spending = monthly_data.groupby("Категория")["Сумма операции"].sum()
        cashback_by_category = {}

        for category, spending in category_spending.items():
            cashback = abs(spending) * 0.01
            cashback_by_category[category] = round(cashback, 2)

        sorted_cashback = dict(
            sorted(cashback_by_category.items(), key=lambda x: x[1], reverse=True)
        )

        logger.info(f"Проанализировано {len(sorted_cashback)} категорий")
        logger.info(
            f"Максимальный кешбэк: {max(sorted_cashback.values()) if sorted_cashback else 0}"
        )

        return json.dumps(sorted_cashback, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка при анализе кешбэка: {e}")
        raise


if __name__ == "__main__":
    sample_data = [
        {
            "Дата операции": "2024-01-15",
            "Категория": "Супермаркеты",
            "Сумма операции": -5000.0,
        },
        {
            "Дата операции": "2024-01-20",
            "Категория": "Рестораны",
            "Сумма операции": -3000.0,
        },
        {
            "Дата операции": "2024-02-10",
            "Категория": "Супермаркеты",
            "Сумма операции": -4000.0,
        },
        {"Дата операции": "2024-01-25", "Категория": "АЗС", "Сумма операции": -2000.0},
    ]

    result = analyze_cashback_categories(sample_data, 2024, 1)
    print("Результат анализа:")
    print(result)
