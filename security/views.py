from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import views as django_views
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

from .forms import SignupForm, LoginForm, ChangePasswordForm


UserModel = get_user_model()


class SignupView(FormView):
    template_name = 'security/signup.html'
    extra_context = {'title': _('Signup')}
    form_class = SignupForm
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


INTERNAL_SIGNUP_VERIFY_URL_TOKEN = 'done'
INTERNAL_SIGNUP_VERIFY_SESSION_TOKEN = '_signup_verify_token'


class SignupVerifyView(TemplateView):
    template_name = 'security/signup_verify.html'
    extra_context = {'title': _('Signup Verify')}
    token_generator = default_token_generator

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
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
            if token == INTERNAL_SIGNUP_VERIFY_URL_TOKEN:
                session_token = self.request.session.get(
                    INTERNAL_SIGNUP_VERIFY_SESSION_TOKEN
                )
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink = True
                    self.user.is_active = True
                    self.user.save()
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_SIGNUP_VERIFY_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, INTERNAL_SIGNUP_VERIFY_URL_TOKEN
                    )
                    return HttpResponseRedirect(redirect_url)

        return self.render_to_response(self.get_context_data())


class LoginView(django_views.LoginView):
    template_name = 'security/login.html'
    extra_context = {'title': _('Login')}
    authentication_form = LoginForm


class LogoutView(django_views.LogoutView):
    pass


class ChangePasswordView(django_views.PasswordChangeView):
    template_name = 'security/change_password.html'
    extra_context = {'title': _('Change Password')}
    form_class = ChangePasswordForm
    success_url = reverse_lazy('change_password_done')


class ChangePasswordDoneView(django_views.PasswordChangeDoneView):
    template_name = 'security/change_password_done.html'
    extra_context = {'title': _('Change Password Done')}
