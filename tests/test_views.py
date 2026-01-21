from unittest.mock import patch
from src.views import veb_json
import json


@patch("src.views.currency_of_valuets")
@patch("src.views.currency_stoks")
def test_main_view_output(mock_stocks, mock_currencies, sample_df, sample_user_settings):
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}, {"stock": "GOOGL", "price": 2500.0}]
    mock_currencies.return_value = [{"currency": "USD", "rate": 73.0}, {"currency": "EUR", "rate": 86.0}]

    result = veb_json()
    data = json.loads(result)

    assert isinstance(data, dict)
    assert isinstance(data["greeting"], str)
    assert isinstance(data["cards"], list)
    assert isinstance(data["top_transactions"], list)
    assert data["currency_of_valuets"] == mock_currencies.return_value
    assert data["currency_stoks"] == mock_stocks.return_value