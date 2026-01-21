# test_utils_fixed.py
import json
import os
import sys
from unittest.mock import mock_open, patch

import pandas as pd

# Мокаем ВСЕ перед импортом
with patch("pandas.read_excel") as mock_read_excel:
    # Создаем фейковый DataFrame
    fake_df = pd.DataFrame(
        {
            "Номер карты": ["*1111", "*2222"],
            "Сумма платежа": [-1000, -500],
            "Категория": ["Food", "Transport"],
            "Дата платежа": ["2023-01-01", "2023-01-02"],
            "Описание": ["A", "B"],
        }
    )
    mock_read_excel.return_value = fake_df

    with patch("dotenv.load_dotenv"):
        with patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(
                    {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
                )
            ),
        ):
            with patch(
                "json.load",
                return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]},
            ):
                # Теперь импортируем
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
                from src.utils import all_cards, top_transactions


def test_all_cards():
    """Тест all_cards с тестовыми данными"""
    df = pd.DataFrame(
        {
            "Номер карты": ["*1111", "*2222", "*1111"],
            "Сумма платежа": [-1000, -500, -300],
            "Категория": ["Food", "Transport", "Food"],
        }
    )

    result = all_cards(df)

    assert len(result) == 2
    assert result[0]["last_digits"] == "*2222"  # Сортировка по возрастанию
    assert result[0]["total_spent"] == 500.0
    assert result[0]["cashback"] == 5.0
    print("✅ all_cards")


def test_top_transactions():
    """Тест top_transactions"""
    df = pd.DataFrame(
        {
            "Дата платежа": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Сумма платежа": [-5000, -1000, -3000],
            "Категория": ["Food", "Transport", "Food"],
            "Описание": ["A", "B", "C"],
        }
    )

    result = top_transactions(df)

    assert len(result) == 3
    assert result[0]["amount"] == 5000  # Наибольшая сумма первая
    assert result[1]["amount"] == 3000
    assert result[2]["amount"] == 1000
    print("✅ top_transactions")


def test_edge_cases():
    """Тест граничных случаев"""
    # Пустой DataFrame
    df_empty = pd.DataFrame(columns=["Номер карты", "Сумма платежа", "Категория"])
    assert all_cards(df_empty) == []

    # Только положительные
    df_positive = pd.DataFrame(
        {"Номер карты": ["*1111"], "Сумма платежа": [1000], "Категория": ["Food"]}
    )
    assert all_cards(df_positive) == []
    print("✅ Граничные случаи")


if __name__ == "__main__":
    test_all_cards()
    test_top_transactions()
    test_edge_cases()
    print("\n🎉 Все тесты utils пройдены!")
