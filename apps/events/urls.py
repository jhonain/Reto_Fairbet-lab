from django.urls import path
from .views import EventosListView

urlpatterns = [
    path("", EventosListView.as_view(), name="eventos-lista"),
]
