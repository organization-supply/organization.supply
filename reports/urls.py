from django.urls import include, path, reverse

from reports import views

urlpatterns = [path("", views.reports_index, name="reports_index")]
