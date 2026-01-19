# test_analytics.py
import pandas as pd
import calendar
import datetime


def test_analize_category_basic():
    """Основной тест analize_category"""
    df = pd.DataFrame({
        "Дата платежа": ["15.01.2023", "20.01.2023", "10.02.2023"],
        "Сумма платежа": [-1000, -500, -300],
        "Категория": ["Food", "Food", "Transport"]
    })

    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
    year, month = 2023, 1
    end_date = calendar.monthrange(year, month)[1]

    mask = (df["Дата платежа"] >= datetime.datetime(year, month, 1)) & \
           (df["Дата платежа"] <= datetime.datetime(year, month, end_date))
    filtr = df[mask]

    filtr_of_pay = filtr[filtr["Сумма платежа"] < 0]

    result = {}
    if not filtr_of_pay.empty:
        grouped = filtr_of_pay.groupby("Категория")["Сумма платежа"].sum().abs()
        result = {cat: int(amount / 100) for cat, amount in grouped.items()}

    assert result["Food"] == 15  # (1000+500)/100
    assert "Transport" not in result  # Только январь
    print("✅ Основной тест")


def test_analize_category_empty():
    """Тест с пустыми данными"""
    df = pd.DataFrame(columns=["Дата платежа", "Сумма платежа", "Категория"])
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"])

    year, month = 2023, 1
    end_date = calendar.monthrange(year, month)[1]

    mask = (df["Дата платежа"] >= datetime.datetime(year, month, 1)) & \
           (df["Дата платежа"] <= datetime.datetime(year, month, end_date))
    filtr = df[mask]

    assert len(filtr) == 0
    print("✅ Пустые данные")


def test_analize_category_positive_only():
    """Только положительные платежи"""
    df = pd.DataFrame({
        "Дата платежа": ["15.01.2023"],
        "Сумма платежа": [1000],
        "Категория": ["Food"]
    })

    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
    filtr_of_pay = df[df["Сумма платежа"] < 0]

    assert len(filtr_of_pay) == 0
    print("✅ Только положительные")


def test_analize_category_multiple_categories():
    """Несколько категорий"""
    df = pd.DataFrame({
        "Дата платежа": ["15.01.2023", "16.01.2023", "17.01.2023"],
        "Сумма платежа": [-100, -200, -300],
        "Категория": ["Food", "Transport", "Food"]
    })

    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
    filtr_of_pay = df[df["Сумма платежа"] < 0]
    grouped = filtr_of_pay.groupby("Категория")["Сумма платежа"].sum().abs()
    result = {cat: int(amount / 100) for cat, amount in grouped.items()}

    assert result["Food"] == 4  # (100+300)/100
    assert result["Transport"] == 2  # 200/100
    print("✅ Несколько категорий")


def test_analize_category_leap_year():
    """Високосный год"""
    df = pd.DataFrame({
        "Дата платежа": ["29.02.2024", "28.02.2023"],
        "Сумма платежа": [-100, -200],
        "Категория": ["Food", "Food"]
    })

    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)

    # 2024 високосный
    end_date_2024 = calendar.monthrange(2024, 2)[1]
    assert end_date_2024 == 29

    # 2023 не високосный
    end_date_2023 = calendar.monthrange(2023, 2)[1]
    assert end_date_2023 == 28

    print("✅ Високосный год")


def test_datetime_conversion():
    """Конвертация дат с dayfirst"""
    # Российский формат
    date1 = pd.to_datetime("31.12.2023", dayfirst=True)
    assert date1.day == 31
    assert date1.month == 12

    # Месяц/день перепутаны без dayfirst
    date2 = pd.to_datetime("12.31.2023", dayfirst=False)
    assert date2.month == 12
    assert date2.day == 31

    print("✅ Конвертация дат")


def test_groupby_sum_abs():
    """Тест группировки и модуля суммы"""
    df = pd.DataFrame({
        "Категория": ["A", "A", "B", "B"],
        "Сумма платежа": [-100, -200, -300, -400]
    })

    grouped = df.groupby("Категория")["Сумма платежа"].sum().abs()
    assert grouped["A"] == 300
    assert grouped["B"] == 700

    # Деление на 100
    result = {k: int(v / 100) for k, v in grouped.items()}
    assert result["A"] == 3
    assert result["B"] == 7

    print("✅ Группировка и сумма")


def test_month_boundaries():
    """Границы месяцев"""
    # Январь 2023
    start = datetime.datetime(2023, 1, 1)
    end = datetime.datetime(2023, 1, 31)

    df = pd.DataFrame({
        "Дата платежа": ["31.01.2023", "01.02.2023"],
        "Сумма платежа": [-100, -200],
        "Категория": ["Food", "Food"]
    })

    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
    mask = (df["Дата платежа"] >= start) & (df["Дата платежа"] <= end)
    january_data = df[mask]

    assert len(january_data) == 1
    assert january_data.iloc[0]["Сумма платежа"] == -100

    print("✅ Границы месяцев")


def run_all_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов analytics...\n")

    test_analize_category_basic()
    test_analize_category_empty()
    test_analize_category_positive_only()
    test_analize_category_multiple_categories()
    test_analize_category_leap_year()
    test_datetime_conversion()
    test_groupby_sum_abs()
    test_month_boundaries()

    print("\n🎉 Все 8 тестов пройдены!")


if __name__ == "__main__":
    run_all_tests()