from django.forms import Form, DecimalField


class ExchangeRateForm(Form):
    exchange_value = DecimalField(max_digits=10, decimal_places=2, label="Exchange value in $")
