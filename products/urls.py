from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('history/', views.history, name='history'),
    path('save-daily/', views.save_daily_record, name='save_daily_record'),
    path('clear-all/', views.clear_all, name='clear_all'),
    path('stats/', views.get_stats, name='stats'),
    
    # Справочник
    path('catalog/', views.catalog_view, name='catalog'),
    
    # Отчёты
    path('reports/', views.report_products, name='report_products'),
    path('reports/product/<str:product_name>/', views.report_product, name='report_product'),
    path('reports/period/', views.report_period, name='report_period'),
]