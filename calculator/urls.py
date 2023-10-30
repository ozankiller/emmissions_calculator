from django.urls import path
from calculator import views

urlpatterns = [
    path(
        "calculator/register_emmission_factor",
        views.register_emmission_factors,
        name="register_emission_factors",
    ),
    path(
        "calculator/read_emmission_records",
        views.read_emmission_records,
        name="read_emmission_records",
    ),
    path("calculator/get_emmissions", views.get_emmissions, name="get_emmissions"),
]
