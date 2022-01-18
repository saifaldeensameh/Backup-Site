from django.urls import path
from . import views
from django.contrib.auth import views as django_views
urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('logout/',django_views.LogoutView.as_view(),name='logout'),
    path('login/', django_views.LoginView.as_view(template_name = 'login.html'), name='login'),
    path('settings/change_password/', django_views.PasswordChangeView.as_view(template_name='change_password.html'), name='password_change'),
    path('settings/change_password/done/', django_views.PasswordChangeDoneView.as_view(template_name='change_password_done.html'),name='password_change_done')

]