from django.contrib import admin
from django.urls import path, include
from core.views import import_page
from rest_framework.authtoken import views as token_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', token_views.obtain_auth_token),  # Add this line
    path('', import_page, name='home'),
]