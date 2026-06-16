from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),          # The admin panel at /admin/
    path('', include('shop.urls')),           # Everything else goes to shop/urls.py
]

# This line makes uploaded images accessible during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)