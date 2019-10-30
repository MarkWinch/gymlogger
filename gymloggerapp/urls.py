from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('settings/edit_profile', views.user_settings_edit_profile, name='user_settings_edit_profile'),
    path('settings/change_password', views.user_settings_change_password, name='user_settings_change_password'),
    path('settings/delete_account', views.user_settings_delete_account, name='user_settings_delete_account'),
    path('', views.name_list, name='name_list'),
    path('<int:exercisegroup_id>/', views.set_forms, name='set_forms'),
    path('<int:exercisegroup_id>/<str:setgroup_id>/', views.edit_sets, name='edit_sets'),
    path('graph/<int:exercisegroup_id>/', views.graph_page, name='graph_page'),
    path('api/data/weight/<int:exercisegroup_id>/', views.get_data_weight, name='get_data_weight'),
    path('api/data/volume/<int:exercisegroup_id>/', views.get_data_volume, name='get_data_volume'),
    path('api/data/weightperworkout/<int:exercisegroup_id>/', views.get_data_weight_workout, name='get_data_weight_workout'),
    path('api/data/volumeperworkout/<int:exercisegroup_id>/', views.get_data_volume_workout, name='get_data_volume_workout')
    
]

