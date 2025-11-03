from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import api

urlpatterns = [
    path('api/v1/', api.api.urls)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
