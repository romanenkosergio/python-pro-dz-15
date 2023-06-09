import abc
import dataclasses
import enum
import os

import requests


class ExchangeCodes(enum.Enum):
    USD = 840
    EUR = 978
    UAH = 980


@dataclasses.dataclass(frozen=True)
class SellBuy:
    sell: float
    buy: float | None


def find_currency(json_data, currency_name):
    if currency_name in json_data:
        return json_data[currency_name]
    else:
        return None


def find_first_element_by_value(lst, key, value):
    for item in lst:
        if key in item and item[key] == value:
            return item
    return None


class ExchangeBase(abc.ABC):
    """
    Base class for exchange providers, should define get_rate() method
    """

    def __init__(self, vendor, currency_a, currency_b):
        self.vendor = vendor
        self.currency_a = currency_a
        self.currency_b = currency_b
        self.pair: SellBuy = None

    @abc.abstractmethod
    def get_rate(self):
        raise NotImplementedError("Method get_rate() is not implemented")


class MonoExchange(ExchangeBase):
    def get_rate(self):
        a_code = ExchangeCodes[self.currency_a].value
        b_code = ExchangeCodes[self.currency_b].value
        r = requests.get("https://api.monobank.ua/bank/currency")
        r.raise_for_status()
        for rate in r.json():
            currency_code_a = rate["currencyCodeA"]
            currency_code_b = rate["currencyCodeB"]
            if currency_code_a == a_code and currency_code_b == b_code:
                self.pair = SellBuy(rate["rateSell"], rate["rateBuy"])

                return


class PrivatExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get(
            "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
        )
        r.raise_for_status()
        for rate in r.json():
            if rate["ccy"] == self.currency_a and rate["base_ccy"] == self.currency_b:
                self.pair = SellBuy(float(rate["sale"]), float(rate["buy"]))


class NBUExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json")
        r.raise_for_status()
        for rate in r.json():
            if rate["cc"] == self.currency_a:
                self.pair = SellBuy(float(rate["rate"]), 0)


class VkurseExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get("https://vkurse.dp.ua/course.json")
        r.raise_for_status()
        rate = find_currency(r.json(), self.currency_a)
        if rate:
            self.pair = SellBuy(float(rate["sale"]), float(rate["buy"]))


class MinfinExchange(ExchangeBase):
    def get_rate(self):
        r = requests.get("https://minfin.com.ua/api/currency/simple/?base=UAH&list=usd,eur")
        r.raise_for_status()
        rate = r.json()["data"][self.currency_a]["midbank"]
        if rate:
            self.pair = SellBuy(float(rate["sell"]["val"]), float(rate["buy"]["val"]))
