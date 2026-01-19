import calendar

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def read_excel_file(road_to_excel_file: str):
    """возврощает excel файлы в ввиде словоря"""
    df = pd.read_excel(road_to_excel_file)
    return df


def analize_category(df, year: int, month: int):
    '''
    выводит все платежи по выбранной категории, за указанный месяц
    '''
    end_date = calendar.monthrange(year, month)[1]
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True)
    filtr = df.loc[df["Дата платежа"] >= f"{year}-{month}-01"].loc[
        df["Дата платежа"] <= f"{year}-{month}-{end_date}"
    ]
    filtr_of_pay = filtr[filtr["Сумма платежа"] < 0]
    filtr_of_cat = filtr_of_pay.groupby("Категория")
    sum_of_cat = filtr_of_cat["Сумма платежа"].sum().abs()
    sum_of_cat_dict = sum_of_cat.to_dict()
    result = {}
    for key, value in sum_of_cat_dict.items():
        result[key] = int(value / 100)
    return result
