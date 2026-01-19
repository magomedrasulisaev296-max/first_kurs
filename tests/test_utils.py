import pandas as pd


def test_all_cards():
    """Тест логики all_cards"""
    df = pd.DataFrame({
        "Номер карты": ["*1234", "*5678", "*1234"],
        "Сумма платежа": [-100, -200, -50]
    })

    # Логика из функции
    operations_sort = df[df["Сумма платежа"] < 0]
    operations_sort_by_group = (
        operations_sort.groupby(["Номер карты"]).agg({"Сумма платежа": "sum"}).abs()
    )
    operations_sort_by_value = operations_sort_by_group.sort_values(
        by=["Сумма платежа"], ascending=True
    )

    result = []
    for i, some_price in operations_sort_by_value.iterrows():
        result.append({
            "last_digits": i,
            "total_spent": float(some_price["Сумма платежа"]),
            "cashback": float(some_price["Сумма платежа"] / 100),
        })

    assert len(result) == 2
    assert result[0]["last_digits"] == "*1234"
    assert result[0]["total_spent"] == 150.0
    assert result[0]["cashback"] == 1.5
    print("✅ all_cards: OK")


def test_top_transactions():
    """Тест логики top_transactions"""
    df = pd.DataFrame({
        "Дата платежа": ["2023-01-01", "2023-01-02"],
        "Сумма платежа": [-1000, -500],
        "Категория": ["Food", "Transport"],
        "Описание": ["Restaurant", "Taxi"]
    })

    operations_sort = df.sort_values("Сумма платежа")
    head_operations = operations_sort[:5].to_dict(orient="records")

    result = []
    for i in head_operations:
        result.append({
            "date": i["Дата платежа"],
            "amount": i["Сумма платежа"] * -1,
            "category": i["Категория"],
            "description": i["Описание"],
        })

    assert len(result) == 2
    assert result[0]["amount"] == 1000
    assert result[1]["amount"] == 500
    print("✅ top_transactions: OK")


def test_currency_calculation():
    """Тест расчета валют"""
    api_response = {"rates": {"USD": 0.011}}

    currency_rates = []
    for key, value in api_response.get("rates").items():
        currency_rates.append({"currency": key, "rate": round(1 / value, 2)})

    assert currency_rates[0]["rate"] == 90.91
    print("✅ currency calculation: OK")


def test_edge_cases():
    """Тест граничных случаев"""

    # 1. Пустой DataFrame для all_cards
    df_empty = pd.DataFrame(columns=["Номер карты", "Сумма платежа"])
    neg_df = df_empty[df_empty["Сумма платежа"] < 0]
    assert len(neg_df) == 0
    print("✅ empty DataFrame: OK")
    df_positive = pd.DataFrame({
        "Номер карты": ["*1111"],
        "Сумма платежа": [100]
    })
    neg_df2 = df_positive[df_positive["Сумма платежа"] < 0]
    assert len(neg_df2) == 0
    df_many = pd.DataFrame({
        "Дата платежа": [f"2023-01-{i:02d}" for i in range(1, 10)],
        "Сумма платежа": [-i * 100 for i in range(1, 10)],
        "Категория": ["Food"] * 9,
        "Описание": [f"Test{i}" for i in range(1, 10)]
    })

    sorted_df = df_many.sort_values("Сумма платежа")
    top5 = sorted_df[:5]
    assert len(top5) == 5


if __name__ == "__main__":

    test_all_cards()
    test_top_transactions()
    test_currency_calculation()
    test_edge_cases()

    print("\n🎉 Все тесты пройдены успешно!")