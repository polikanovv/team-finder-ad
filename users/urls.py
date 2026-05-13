from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('list/', views.users_list, name='list'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('skills/', views.skills_autocomplete, name='skills_autocomplete'),
    path('skills/add/', views.add_skill, name='add_skill'),
    path('skills/<int:skill_id>/remove/', views.remove_skill, name='remove_skill'),
    path('<int:user_id>/', views.user_detail, name='detail'),
]
