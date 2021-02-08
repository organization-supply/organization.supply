from django.urls import include, path, reverse, re_path
from reports import views

urlpatterns = [
    path("", views.reports_index, name="reports_index"),
    re_path('(?P<date>\d{4}-\d{2}-\d{2})/', views.reports_at_date, name="reports_at_date")
]