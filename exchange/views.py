import datetime
import decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render

from .forms import ExchangeRateForm
from .models import Rate


class DecimalAsFloatJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)


# Create your views here.


def index(request):
    current_date = datetime.date.today()
    current_rates = Rate.objects.filter(date=current_date).all().values()
    return JsonResponse(
        {"current_rates": list(current_rates)}, encoder=DecimalAsFloatJSONEncoder
    )


def calculate_rate(request):
    if request.method == "GET":
        form = ExchangeRateForm()
    else:
        form = ExchangeRateForm(request.POST)
        if form.is_valid():
            exchange_value = form.cleaned_data["exchange_value"]
            best_rate = Rate.objects.order_by("-buy").first()
            result = float(exchange_value * best_rate.buy)
            return render(request, "calculate_rate.html", {"form": form, "is_calculated": True, "bank_name": best_rate.vendor, "rate": best_rate.buy, "result": result})

    return render(request, "calculate_rate.html", {"form": form})