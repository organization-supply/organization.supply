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
from organizations.backends import invitation_backend

from organization import views

urlpatterns = [
    # Index
    path("", views.index, name="index"),
    # User urls
    path("user/", include("user.urls")),
    path("user/", include("django.contrib.auth.urls")),
    # Organization invites
    path("invitations/", include(invitation_backend().get_urls())),
    # Admin
    path("admin/", admin.site.urls),
    # Organization urls (listed last, so we the others have priority)
    path("create", views.organization_create, name="create_organization"),
    path("<slug:organization>/", include("organization.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
