from django.urls import path

from . import views


urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/verify/pending', views.SignupVerifyPendingView.as_view(),
         name='signup_verify_pending'),
    path('signup/verify/<uidb64>/<token>/', views.SignupVerifyView.as_view(),
         name='signup_verify'),

    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),
    path('change-password/done/', views.ChangePasswordDoneView.as_view(),
         name='change_password_done'),

    path('reset-password/', views.ResetPasswordView.as_view(),
         name='reset_password'),
    path('reset-password/verify/pending/',
         views.ResetPasswordVerifyPendingView.as_view(),
         name='reset_password_verify_pending'),
    path('reset-password/verify/<uidb64>/<token>/',
         views.ResetPasswordVerifyView.as_view(),
         name='reset_password_verify'),
    path('reset-password/done/', views.ResetPasswordDoneView.as_view(),
         name='reset_password_done')
]
