from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('legislators/', views.legislators_list, name='legislators-list'),
    path('legislators/<int:govtrack_id>/', views.legislator_detail, name='legislator-detail'),
    path('legislators/<int:govtrack_id>/notes/', views.update_notes, name='update-notes'),
    path('stats/age/', views.age_stats, name='age-stats'),
    path('legislators/<int:govtrack_id>/weather/', views.weather_info, name='weather-info'),
]