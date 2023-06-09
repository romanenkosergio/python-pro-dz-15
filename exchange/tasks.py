import datetime

from .models import Rate
from .exchange_provider import MonoExchange, PrivatExchange, NBUExchange, VkurseExchange, MinfinExchange

from celery import shared_task


@shared_task
def start_exchange(vendor, currency_a, currency_b):
    current_date = datetime.date.today()
    is_rate_exists = Rate.objects.filter(
        date=current_date, vendor=vendor, currency_a=currency_a, currency_b=currency_b
    ).exists()
    if is_rate_exists:
        print(
            f"Rate already exists for {current_date} {vendor} {currency_a} {currency_b}"
        )
        return

    if vendor == "privat":
        exchange = PrivatExchange(vendor, currency_a, currency_b)
    elif vendor == "mono":
        exchange = MonoExchange(vendor, currency_a, currency_b)
    elif vendor == "vkurse":
        exchange = VkurseExchange(vendor, currency_a, currency_b)
    elif vendor == "minfin":
        exchange = MinfinExchange(vendor, currency_a, currency_b)
    elif vendor == "nbu":
        exchange = NBUExchange(vendor, currency_a, currency_b)
    exchange.get_rate()
    Rate.objects.get_or_create(
        date=current_date,
        vendor=vendor,
        currency_a=currency_a,
        currency_b=currency_b,
        defaults={"sell": exchange.pair.sell, "buy": exchange.pair.buy},
    )

