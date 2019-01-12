from django.urls import path

from .views import (
    SignupView, SignupVerifyPendingView, SignupVerifyView,
    LoginView, LogoutView,
    ChangePasswordView, ChangePasswordDoneView
)


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/verify/pending', SignupVerifyPendingView.as_view(),
         name='signup_verify_pending'),
    path('signup/verify/<uidb64>/<token>/', SignupVerifyView.as_view(),
         name='signup_verify'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('change-password/', ChangePasswordView.as_view(),
         name='change_password'),
    path('change-password/done/', ChangePasswordDoneView.as_view(),
         name='change_password_done')
]
