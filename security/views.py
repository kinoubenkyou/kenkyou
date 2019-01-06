from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .forms import SignupForm


class SignupView(FormView):
    template_name = 'security/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('signup_done')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class SignupDoneView(TemplateView):
    template_name = 'security/signup_done.html'
