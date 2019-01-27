from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic.base import (
    TemplateResponseMixin, ContextMixin, View, TemplateView
)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import KanjiEntry, KanjiLearningRecord


class LearnKanjiView(LoginRequiredMixin, TemplateResponseMixin,
                     View, ContextMixin):
    template_name = 'tutor/learn_kanji.html'
    extra_context = {'title': _('Learn Kanji')}

    def get(self, request):
        user_id = request.user.id

        query_set = (
            KanjiEntry.objects.filter(kanjilearningrecord__user__id=user_id,
                                      kanjilearningrecord__is_learnt=False)
            .exclude(kanjilearningrecord__order=None)
            .order_by('kanjilearningrecord__order')
        )

        if query_set.count() > 0:
            entry = query_set[0]
        else:
            query_set = KanjiEntry.objects.filter(
                kanjilearningrecord__user__id=user_id,
                kanjilearningrecord__is_learnt=False,
                kanjilearningrecord__order=None
            ).order_by('order')

            if query_set.count() > 0:
                entry = query_set[0]
            else:
                return HttpResponseRedirect(reverse_lazy('learn_kanji_done'))

        return self.render_to_response(self.get_context_data(entry=entry))

    def post(self, request):
        query_set = KanjiLearningRecord.objects.filter(
            user_id=request.user.id,
            kanji_entry__id=request.POST['entry_id']
        )

        if query_set.count() == 1:
            record = query_set[0]
            record.is_learnt = True
            record.save()

        return HttpResponseRedirect(reverse_lazy('learn_kanji'))


class LearnKanjiDoneView(TemplateView):
    template_name = 'tutor/learn_kanji_done.html'
    extra_context = {'title': _('Learn Kanji Done')}
