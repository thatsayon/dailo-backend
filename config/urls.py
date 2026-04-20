from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('app.accounts.v1.urls')),
    path('api/v1/creator/', include('app.creator.v1.urls')),
    path('api/v1/administration/', include('app.dashboard.v1.urls')),
    path('api/v1/feed/', include('app.feed.v1.urls')),
]
