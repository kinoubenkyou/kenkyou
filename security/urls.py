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
         name='change_password_done')
]
