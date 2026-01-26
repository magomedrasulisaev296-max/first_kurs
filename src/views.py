import json

from src.utils import (all_cards, currency_of_valuets, currency_stoks, greetings, operations, top_transactions,
                       values_stocks_to_request, values_to_request)


def veb_json() -> str:
    """собирает функции из модуля utils.py и возвращает их в виде еденного json ответ"""
    greeting_ = greetings()
    cards = all_cards(operations)
    top_transactions_ = top_transactions(operations)
    currency_of_valuets_ = currency_of_valuets(values_to_request)
    currency_stoks_ = currency_stoks(values_stocks_to_request)

    final_report = {
        "greeting": greeting_,
        "cards": cards,
        "top_transactions": top_transactions_,
        "currency_of_valuets": currency_of_valuets_,
        "currency_stoks": currency_stoks_,
    }
    return json.dumps(final_report, indent=4)


if __name__ == "__main__":
    print(veb_json())
