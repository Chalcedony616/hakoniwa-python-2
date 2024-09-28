from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('game.urls')),
    path('accounts/', include('game.urls')),  # 追加
]
