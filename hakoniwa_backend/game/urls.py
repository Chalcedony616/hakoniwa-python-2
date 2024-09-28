from django.urls import path
from .views import register, create_island, list_islands, island_detail, login, update_plans, get_island_logs, global_recent_logs, get_histories, get_turn_info

urlpatterns = [
    path('register/', register, name='register'),
    path('create_island/', create_island, name='create_island'),
    path('islands/', list_islands, name='list_islands'),
    path('islands/<int:pk>/', island_detail, name='island_detail'),
    path('login/', login, name='login'),
    path('islands/<int:pk>/plans/', update_plans, name='update_plans'),
    path('islands/<int:island_id>/logs/', get_island_logs, name='get_island_logs'),
    path('global-logs/', global_recent_logs, name='global_recent_logs'),
    path('histories/', get_histories, name='get_histories'),
    path('turn_info/', get_turn_info, name='get_turn_info'),
]
