from django.urls import include, path, reverse

from deck import views

urlpatterns = [path("", views.deck_index, name="deck_index")]
