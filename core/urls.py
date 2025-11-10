from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="core-main"),
    path('login/', views.login_view, name="login"),
    path('profile/', views.user_profile, name="user-profile"),
    path('signup/', views.signup, name='signup'),  
    path('signin/', views.signin, name='signin'),  
    path('signout/', views.signout, name='signout'),
    ]
