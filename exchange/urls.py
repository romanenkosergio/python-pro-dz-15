from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("calculate_rate", views.calculate_rate, name="calculate_rate"),
]
