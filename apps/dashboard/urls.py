from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_operador, name='dashboard-panel'),
    path('eventos/', views.gestion_eventos, name='dashboard-eventos'),
    path('eventos/<uuid:evento_id>/', views.evento_detalle, name='dashboard-evento-detalle'),
    path('apuestas/', views.gestion_apuestas, name='dashboard-apuestas'),
    path('limites/', views.gestion_limites, name='dashboard-limites'),
    path('acciones/', views.gestion_acciones, name='dashboard-acciones'),
    path('alertas/', views.gestion_alertas, name='dashboard-alertas'),
    path('reporte.csv', views.reporte_csv, name='dashboard-reporte-csv'),
]
