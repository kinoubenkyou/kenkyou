from django.urls import path

from .views import SignupView, SignupVerifyView, SignupDoneView


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/verify/', SignupVerifyView.as_view(), name='signup_verify'),
    path('signup/done/<uidb64>/<token>/', SignupDoneView.as_view(),
         name='signup_done')
]
