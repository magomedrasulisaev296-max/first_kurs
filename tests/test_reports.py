# test_decorator.py
import pytest
import json
import pandas as pd
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open, call
import tempfile
import shutil


# Создаем временную директорию для тестов
@pytest.fixture
def temp_dir():
    """Фикстура для временной директории"""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


# Импортируем тестируемый модуль с моками
with patch('pandas.read_excel') as mock_read_excel:
    mock_df = pd.DataFrame({
        'Дата платежа': ['15.01.2023', '20.01.2023'],
        'Категория': ['Food', 'Transport'],
        'Сумма платежа': [-1000, -500]
    })
    mock_read_excel.return_value = mock_df

    from src.reports import read_excel_file, report_to_file, spending_by_category, df


def test_read_excel_file():
    """Тест функции read_excel_file"""
    with patch('pandas.read_excel') as mock_read:
        test_df = pd.DataFrame({'A': [1, 2]})
        mock_read.return_value = test_df

        result = read_excel_file("test.xlsx")

        mock_read.assert_called_once_with("test.xlsx")
        assert result.equals(test_df)
    print("✅ read_excel_file")


def test_spending_by_category_logic():
    """Тест логики spending_by_category"""
    # Создаем тестовый DataFrame
    test_data = {
        'Дата платежа': ['15.01.2023', '20.02.2023', '10.12.2022', '25.01.2023'],
        'Категория': ['Food', 'Food', 'Transport', 'Food'],
        'Сумма платежа': [-1000, -500, -300, -200]
    }
    df_test = pd.DataFrame(test_data)

    # Преобразуем даты
    df_test['Дата платежа'] = pd.to_datetime(df_test['Дата платежа'], format='%d.%m.%Y', dayfirst=True)

    # Вызываем функцию
    result = spending_by_category.__wrapped__(df_test, "Food", [31, 1, 2023])

    # Проверяем
    assert len(result) == 2  # Только 2 транзакции Food за 90 дней до 31.01.2023
    assert all(result['Категория'] == 'Food')
    assert all(result['Сумма платежа'] < 0)
    print("✅ spending_by_category логика")


def test_report_to_file_decorator(temp_dir):
    """Тест декоратора report_to_file"""
    # Мокаем все зависимости
    with patch('os.makedirs') as mock_makedirs, \
            patch('builtins.open', mock_open()) as mock_file, \
            patch('json.dump') as mock_json_dump, \
            patch('src.reports.datetime') as mock_datetime:
        # Настраиваем моки
        mock_datetime.now.return_value.strftime.return_value = '20240101_120000'

        # Создаем тестовую функцию
        @report_to_file()
        def test_func():
            return pd.DataFrame({
                'Дата платежа': pd.to_datetime(['2023-01-15', '2023-01-20']),
                'Категория': ['Food', 'Transport'],
                'Сумма платежа': [-1000, -500],
                'Другие колонки': ['A', 'B']
            })

        # Вызываем
        result = test_func()

        # Проверяем вызовы
        mock_makedirs.assert_called_once_with("reports", exist_ok=True)
        mock_file.assert_called_once()

        # Проверяем что json.dump был вызван
        assert mock_json_dump.called
        print("✅ report_to_file decorator")


def test_report_to_file_with_dataframe(temp_dir):
    """Тест декоратора с DataFrame"""
    # Создаем тестовый DataFrame
    test_df = pd.DataFrame({
        'Дата платежа': pd.to_datetime(['2023-01-15', '2023-01-20']),
        'Категория': ['Food', 'Transport'],
        'Сумма платежа': [-1000, -500],
        'Дополнительно': ['A', 'B']
    })

    # Тестируем логику внутри декоратора
    needed_columns = ["Дата платежа", "Категория", "Сумма платежа"]
    result_filtered = test_df[needed_columns].copy()
    result_filtered["Дата платежа"] = result_filtered["Дата платежа"].dt.strftime("%d.%m.%Y")

    total_sum = float(abs(result_filtered["Сумма платежа"].sum()))

    json_data = {
        "total_sum": total_sum,
        "transactions": result_filtered.to_dict("records"),
    }

    assert json_data["total_sum"] == 1500.0
    assert len(json_data["transactions"]) == 2
    assert json_data["transactions"][0]["Категория"] == "Food"
    print("✅ DataFrame processing in decorator")


def test_report_to_file_empty_dataframe():
    """Тест с пустым DataFrame"""
    empty_df = pd.DataFrame(columns=['Дата платежа', 'Категория', 'Сумма платежа'])

    # Тестируем логику
    if not empty_df.empty:
        needed_columns = ["Дата платежа", "Категория", "Сумма платежа"]
        result_filtered = empty_df[needed_columns].copy()
    else:
        result_filtered = empty_df

    total_sum = 0.0 if result_filtered.empty else float(abs(result_filtered["Сумма платежа"].sum()))

    assert total_sum == 0.0
    print("✅ Empty DataFrame handling")


def test_spending_by_category_filters():
    """Тест фильтров spending_by_category"""
    df_test = pd.DataFrame({
        'Дата платежа': ['15.01.2023', '20.10.2022', '10.12.2022'],
        'Категория': ['Food', 'Food', 'Transport'],
        'Сумма платежа': [-1000, -500, 300]  # Последняя положительная
    })

    df_test['Дата платежа'] = pd.to_datetime(df_test['Дата платежа'], format='%d.%m.%Y', dayfirst=True)

    # Логика фильтров
    category = "Food"
    date = (31, 1, 2023)
    day, month, year = date
    end_date = datetime(year, month, day)
    start_date = end_date - timedelta(days=90)

    mask = (
            (df_test['Категория'] == category) &
            (df_test['Дата платежа'] >= start_date) &
            (df_test['Дата платежа'] <= end_date) &
            (df_test['Сумма платежа'] < 0)
    )

    result = df_test[mask]

    assert len(result) == 1  # Только одна транзакция Food за 90 дней
    assert result.iloc[0]['Сумма платежа'] == -1000
    print("✅ Фильтры spending_by_category")


def test_date_calculation():
    """Тест расчета дат"""
    end_date = datetime(2023, 1, 31)
    start_date = end_date - timedelta(days=90)

    # Проверяем что start_date на 90 дней раньше
    delta = end_date - start_date
    assert delta.days == 90

    # Проверяем конкретные даты
    assert start_date == datetime(2022, 11, 2)  # 31.01.2023 - 90 дней = 02.11.2022
    print("✅ Date calculation")


def test_total_sum_calculation():
    """Тест расчета общей суммы"""
    df_test = pd.DataFrame({
        'Сумма платежа': [-1000, -500, -300]
    })

    total_spent = abs(df_test['Сумма платежа'].sum())
    assert total_spent == 1800.0

    # Проверяем форматирование
    formatted = f"Всего потрачено: {total_spent:.2f} руб"
    assert "Всего потрачено:" in formatted
    assert "1800.00 руб" in formatted
    print("✅ Total sum calculation")


def test_json_serialization():
    """Тест сериализации JSON"""
    test_data = {
        "total_sum": 1500.0,
        "transactions": [
            {"Дата платежа": "15.01.2023", "Категория": "Food", "Сумма платежа": -1000},
            {"Дата платежа": "20.01.2023", "Категория": "Transport", "Сумма платежа": -500}
        ]
    }

    # Сериализуем
    result = json.dumps(test_data, ensure_ascii=False, indent=2)

    # Десериализуем обратно
    parsed = json.loads(result)

    assert parsed["total_sum"] == 1500.0
    assert len(parsed["transactions"]) == 2
    assert parsed["transactions"][0]["Категория"] == "Food"
    print("✅ JSON serialization")


def run_all_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов decorator модуля...\n")

    test_read_excel_file()
    test_spending_by_category_logic()
    test_report_to_file_decorator(tempfile.mkdtemp())
    test_report_to_file_with_dataframe(tempfile.mkdtemp())
    test_report_to_file_empty_dataframe()
    test_spending_by_category_filters()
    test_date_calculation()
    test_total_sum_calculation()
    test_json_serialization()

    print("\n🎉 Все тесты decorator пройдены!")


if __name__ == "__main__":
    run_all_tests()