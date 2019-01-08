from django.urls import path

from .views import (
    SignupView, SignupVerifyView, SignupDoneView, LoginView, LogoutView
)


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/verify/', SignupVerifyView.as_view(), name='signup_verify'),
    path('signup/done/<uidb64>/<token>/', SignupDoneView.as_view(),
         name='signup_done'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
