"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from inventory import views as views_inventory
from organization.views import views_organization

urlpatterns = [
    # Index: redirect to user organization page
    path("", views_inventory.index, name="index"),
    # Static page
    path("help", views_inventory.help, name="help"),
    path("privacy", views_inventory.privacy, name="privacy"),
    path("terms", views_inventory.terms, name="terms"),
    # User urls
    path("user/", include("user.urls")),
    path("user/", include("django.contrib.auth.urls")),
    # Admin
    path("admin/", admin.site.urls),
    path("deck/", include("deck.urls")),
    # Tags
    path(
        "tags/autocomplete",
        views_inventory.TagsAutocomplete.as_view(),
        name="tags-autocomplete",
    ),
    # Organization urls (listed last, so we the others have priority)
    path("create", views_organization.organization_create, name="create_organization"),
    path("<slug:organization>/", include("organization.urls")),
]

# Error pages
handler400 = views_inventory.handle_400
handler403 = views_inventory.handle_403
handler404 = views_inventory.handle_404
handler500 = views_inventory.handle_500


# Static & media for development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )  # pragma: no cover
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )  # pragma: no cover

    # Debug toolbar
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]  # pragma: no cover
