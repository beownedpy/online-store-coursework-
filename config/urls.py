from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
