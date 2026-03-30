from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    path('tasks/create/', views.create_task_view, name='create_task'),
    path('tasks/<int:pk>/update/', views.update_task_view, name='update_task'),
    path('tasks/<int:pk>/delete/', views.delete_task_view, name='delete_task'),
]
