from django.urls import path
from .views import (
    RegistrationView,
    AccountActivationView,

    LoginView,
    LogoutView,

)

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='register-account'),
    path('activate/', AccountActivationView.as_view(), name='activate account'),

    path('login/', LoginView.as_view(), name='log-in'),
    path('logout/', LogoutView.as_view(), name='log-out'),

]