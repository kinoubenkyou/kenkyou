from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import views
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

from . import forms


UserModel = get_user_model()


class SignupView(FormView):
    template_name = 'security/signup.html'
    extra_context = {'title': _('Signup')}
    form_class = forms.SignupForm
    success_url = reverse_lazy('signup_verify_pending')

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'request': self.request,
        }
        form.save(**opts)
        return super().form_valid(form)


class SignupVerifyPendingView(TemplateView):
    template_name = 'security/signup_verify_pending.html'
    extra_context = {'title': _('Signup Verify Pending')}


SIGNUP_VERIFY_URL_FLAG = 'done'
SIGNUP_VERIFY_TOKEN_KEY = '_signup_verify_token'


class SignupVerifyView(TemplateView):
    template_name = 'security/signup_verify.html'
    extra_context = {'title': _('Signup Verify')}
    token_generator = default_token_generator

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validlink'] = self.validlink
        return context

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == SIGNUP_VERIFY_URL_FLAG:
                session_token = self.request.session.get(
                    SIGNUP_VERIFY_TOKEN_KEY
                )
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True
                    self.user.is_active = True
                    self.user.save()
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[SIGNUP_VERIFY_TOKEN_KEY] = token
                    redirect_url = self.request.path.replace(
                        token, SIGNUP_VERIFY_URL_FLAG
                    )
                    return HttpResponseRedirect(redirect_url)

        return self.render_to_response(self.get_context_data())


class LoginView(views.LoginView):
    template_name = 'security/login.html'
    extra_context = {'title': _('Login')}
    authentication_form = forms.LoginForm


class LogoutView(views.LogoutView):
    pass


class ChangePasswordView(views.PasswordChangeView):
    template_name = 'security/change_password.html'
    extra_context = {'title': _('Change Password')}
    form_class = forms.ChangePasswordForm
    success_url = reverse_lazy('change_password_done')


class ChangePasswordDoneView(views.PasswordChangeDoneView):
    template_name = 'security/change_password_done.html'
    extra_context = {'title': _('Change Password Done')}


class ResetPasswordView(views.PasswordResetView):
    template_name = 'security/reset_password.html'
    extra_context = {'title': _('Reset Password')}
    form_class = forms.ResetPasswordForm
    success_url = reverse_lazy('reset_password_verify_pending')
    subject_template_name = 'security/reset_password_verify_subject.txt'
    email_template_name = 'security/reset_password_verify_email.html'


class ResetPasswordVerifyPendingView(views.PasswordResetDoneView):
    template_name = 'security/reset_password_verify_pending.html'
    extra_context = {'title': _('Reset Password Verify Pending')}


RESET_PASSWORD_VERIFY_URL_FLAG = 'set_password'
RESET_PASSWORD_VERIFY_TOKEN_KEY = '_reset_password_token'


class ResetPasswordVerifyView(FormView):
    template_name = 'security/reset_password_verify.html'
    extra_context = {'title': _('Reset Password Verify')}
    form_class = forms.ResetPasswordVerifyForm
    success_url = reverse_lazy('reset_password_done')
    token_generator = default_token_generator

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist,
                ValidationError):
            user = None
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validlink'] = self.validlink
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        del self.request.session[RESET_PASSWORD_VERIFY_TOKEN_KEY]
        return super().form_valid(form)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == RESET_PASSWORD_VERIFY_URL_FLAG:
                session_token = self.request.session.get(
                    RESET_PASSWORD_VERIFY_TOKEN_KEY
                )
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[
                        RESET_PASSWORD_VERIFY_TOKEN_KEY
                    ] = token
                    redirect_url = self.request.path.replace(
                        token,
                        RESET_PASSWORD_VERIFY_URL_FLAG
                    )
                    return HttpResponseRedirect(redirect_url)

        return self.render_to_response(self.get_context_data())


class ResetPasswordDoneView(views.PasswordResetCompleteView):
    template_name = 'security/reset_password_done.html'
    extra_context = {'title': _('Reset Password Done')}
