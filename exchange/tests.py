import json
import pathlib

import pytest
import responses
from django.core.management import call_command
from freezegun import freeze_time

from .exchange_provider import MonoExchange, PrivatExchange, NBUExchange, VkurseExchange, MinfinExchange
from .views import index

root = pathlib.Path(__file__).parent


# Create your tests here.

@pytest.fixture
def mocked():
    def inner(file_name):
        return json.load(open(root / "fixtures" / file_name))

    return inner


@responses.activate
def test_exchange_mono(mocked):
    mocked_response = mocked("mono_response.json")
    responses.get(
        "https://api.monobank.ua/bank/currency",
        json=mocked_response,
    )
    e = MonoExchange("mono", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.4406


def test_privat_rate(mocked):
    mocked_response = mocked("privat_response.json")
    responses.get(
        "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11",
        json=mocked_response,
    )
    e = PrivatExchange("privat", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.45318


def test_nbu_rate(mocked):
    mocked_response = mocked("nbu_response.json")
    responses.get(
        "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json",
        json=mocked_response,
    )
    e = NBUExchange("nbu", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 36.5686


def test_vkurse_rate(mocked):
    mocked_response = mocked("vkurse_response.json")
    responses.get(
        "https://vkurse.dp.ua/course.json",
        json=mocked_response,
    )
    e = VkurseExchange("vkurse", "Dollar", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.3


def test_minfin_rate(mocked):
    mocked_response = mocked("minfin_response.json")
    responses.get(
        "https://minfin.com.ua/api/currency/simple/?base=UAH&list=usd",
        json=mocked_response,
    )
    e = MinfinExchange("minfin", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.3


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "db_init.yaml")


@freeze_time("2022-01-01")
@pytest.mark.django_db
def test_index_view():
    response = index(None)
    assert response.status_code == 200
    assert json.loads(response.content) == {
        "current_rates": [
            {
                "id": 1,
                "date": "2022-01-01",
                "vendor": "mono",
                "currency_a": "USD",
                "currency_b": "EUR",
                "sell": 1.1,
                "buy": 1.2,
            },
            {
                "id": 2,
                "date": "2022-01-01",
                "vendor": "privat",
                "currency_a": "USD",
                "currency_b": "EUR",
                "sell": 1.01,
                "buy": 1.0,
            },
        ]
    }