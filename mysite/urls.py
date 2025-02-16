from django.contrib import admin  # Tuo admin-moduulin
from django.urls import path, include  # Tuo tarvittavat reititystyökalut

urlpatterns = [
    path('admin/', admin.site.urls),  # Tämä rivi aiheuttaa virheen ilman admin-importia
    path('', include('messageboard.urls')),  # Liitetään sovelluksen URL-reitit
]

