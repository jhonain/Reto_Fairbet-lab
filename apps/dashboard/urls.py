from django.urls import path
from .views import DashboardView, ReporteMensualView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("reporte-mensual/", ReporteMensualView.as_view(), name="reporte-mensual"),
]
