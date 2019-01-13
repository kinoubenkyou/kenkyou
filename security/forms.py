from django.contrib.auth import forms as django_forms
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . import models


class SignupForm(django_forms.UserCreationForm):

    class Meta:
        model = models.User
        fields = ("username", "email")
        field_classes = {'username': django_forms.UsernameField}

    def send_mail(self, context, to_email,
                  subject_template_name, email_template_name,
                  from_email=None, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body,
                                               from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name,
                                                 context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def save(self, use_https, request, token_generator=default_token_generator,
             commit=True, domain_override=None, extra_email_context=None):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()

            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            email = user.email
            context = {
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                context, email,
                subject_template_name='security/signup_verify_subject.txt',
                email_template_name='security/signup_verify_email.html'
            )
        return user


class LoginForm(django_forms.AuthenticationForm):
    pass


class ChangePasswordForm(django_forms.PasswordChangeForm):
    pass


class ResetPasswordForm(django_forms.PasswordResetForm):
    pass


class ResetPasswordVerifyForm(django_forms.SetPasswordForm):
    pass
