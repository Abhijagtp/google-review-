from django.contrib import admin
from django.urls import path, include
from apps.business.views import root_view

urlpatterns = [
    path('', root_view, name='root'),
    path('', include('apps.business.urls')),
    path('admin/', admin.site.urls),
]


