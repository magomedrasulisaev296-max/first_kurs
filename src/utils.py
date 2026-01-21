import datetime
import json
import os
import finnhub  # type: ignore
import pandas as pd
import requests

from dotenv import load_dotenv

load_dotenv()


def greetings():
    '''выводит приветсвенное сообщение в зависимости от времени пользователя'''
    now = datetime.datetime.now()
    greeting = ""
    if now.hour < 12:
        greeting += "Good Morning"
    elif now.hour < 18 and now.hour > 12:
        greeting += "Good Afternoon"
    elif now.hour > 18:
        greeting += "Good Evening"
    else:
        greeting += "Good Night"
    return greeting


def read_excel_file(road_to_excel_file: str):
    """возврощает excel файлы в ввиде словоря"""
    df = pd.read_excel(road_to_excel_file)
    return df


operations = read_excel_file(r"data/operations.xlsx")


def all_cards(operations: pd.DataFrame) -> list[dict]:
    '''выводит все номера карт имеющиеся в дата-фрейме(operations)'''
    list_ = []
    operations_sort = operations[operations["Сумма платежа"] < 0]
    operations_sort_by_group = (
        operations_sort.groupby(["Номер карты"]).agg({"Сумма платежа": "sum"}).abs()
    )
    operations_sort_by_value = operations_sort_by_group.sort_values(
        by=["Сумма платежа"], ascending=True
    )
    for i, some_price in operations_sort_by_value.iterrows():
        list_.append(
            {
                "last_digits": i,
                "total_spent": float(some_price["Сумма платежа"]),
                "cashback": float(some_price["Сумма платежа"] / 100),
            }
        )
    return list_


def top_transactions(operations: pd.DataFrame) -> list[dict]:
    '''выводит самые большие транзакции в переданном дата-фрейме'''
    list_ = []
    operations_sort = operations.sort_values("Сумма платежа")
    head_operations = operations_sort[:5].to_dict(orient="records")
    for i in head_operations:
        list_.append(
            {
                "date": i["Дата платежа"],
                "amount": i["Сумма платежа"] * -1,
                "category": i["Категория"],
                "description": i["Описание"],
            }
        )
    return list_


with open("data/user_settings.json", "r", encoding="utf-8") as file:
    data_ = json.load(file)

values_to_request = ", ".join(data_["user_currencies"])
values_stocks_to_request = data_["user_stocks"]


def currency_of_valuets(symbols: str) -> list[dict]:
    '''выдает курс валют к рублю в настоящие время'''
    base = "RUB"
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"

    headers = {"apikey": ("TS9TqEJh2cyBdmsaoAFQqKuBDI4mHBfa")}

    currency_rates = []

    response = requests.get(url, headers=headers, data={})
    print(response.status_code)
    for key, value in response.json().get("rates").items():
        currency_rates.append({"currency": key, "rate": round(1 / value, 2)})
    return currency_rates


def currency_stoks(stocks: str) -> list[dict]:

    '''выдает курс заданных акций в настоящие время'''
    finnhub_client = finnhub.Client(api_key=os.getenv("API_FINNHUB"))

    resalt_stock = []
    for i in stocks:
        quote = finnhub_client.quote(i)
        resalt_stock.append({"stock": i, "price": quote["c"]})
    return resalt_stock
