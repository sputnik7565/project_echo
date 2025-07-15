from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.hub_page, name='hub_page'), # New hub page as the root of the app
    path('generate_report/', views.generate_report_view, name='generate_report'), # New URL for report generation
    path('get_report_progress/', views.get_report_progress, name='get_report_progress'), # New URL for progress tracking
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/delete/', views.delete_report, name='delete_report'), # New URL for deleting reports
    path('reports/<int:report_id>/pdf/', views.report_pdf, name='report_pdf'),
    path('reports/<int:report_id>/download_md/', views.download_markdown_report, name='download_markdown_report'), # New URL for downloading markdown reports
]