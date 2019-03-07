import random
import math
from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import KanjiEntry, KanjiLearningRecord, KanjiTestingRecord


DEFAULT_BASE_INTERVAL = 1
DEFAULT_INTERVAL_RATE = 2


def query_string(**kwargs):
    query_params = []

    for key in kwargs:
        value = kwargs[key]
        if value is not None and value is not False:
            query_params.append(key + '=' + str(value))

    if query_params:
        return '?' + '&'.join(query_params)

    return ''


class LearnKanjiView(LoginRequiredMixin, TemplateView):
    template_name = 'tutor/learn_kanji.html'
    extra_context = {'title': _('Learn Kanji')}

    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        query_set = KanjiEntry.objects.filter(
            kanjilearningrecord__user__id=user_id,
            kanjilearningrecord__is_learnt=False
        ).order_by('order')

        if query_set.count() > 0:
            entry = query_set[0]
        else:
            return HttpResponseRedirect(reverse_lazy('learn_kanji_done'))

        return self.render_to_response(self.get_context_data(entry=entry))

    def post(self, request, *args, **kwargs):
        entry_id = request.POST['entry_id']

        query_set = KanjiLearningRecord.objects.filter(
            user_id=request.user.id,
            kanji_entry__id=entry_id
        )

        learning_record = query_set.get()
        learning_record.is_learnt = True
        learning_record.save()

        KanjiTestingRecord.objects.create(
            kanji_entry=KanjiEntry.objects.get(pk=entry_id),
            user=request.user
        )

        return HttpResponseRedirect(reverse_lazy('learn_kanji'))


class LearnKanjiDoneView(TemplateView):
    template_name = 'tutor/learn_kanji_done.html'
    extra_context = {'title': _('Learn Kanji Done')}


class TestKanjiView(LoginRequiredMixin, TemplateView):
    template_name = 'tutor/test_kanji.html'
    extra_context = {'title': _('Test Kanji')}

    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        query_set = KanjiEntry.objects.filter(
            kanjilearningrecord__user__id=user_id,
            kanjilearningrecord__is_learnt=True,
            kanjitestingrecord__user__id=user_id,
            kanjitestingrecord__test_date__lte=date.today()
        ).order_by('order')

        if query_set.count() > 0:
            tested_entry = query_set[0]
        else:
            return HttpResponseRedirect(reverse_lazy('test_kanji_done'))

        choices = [tested_entry]
        query_set = KanjiEntry.objects.exclude(id=tested_entry.id)
        other_entry_count = query_set.count()

        if other_entry_count > 2:
            other_choice_count = 3
        else:
            other_choice_count = other_entry_count

        for i in random.sample(range(other_entry_count),
                               other_choice_count):
            if bool(random.getrandbits(1)):
                choices.append(query_set[i])
            else:
                choices.insert(0, query_set[i])

        return self.render_to_response(
            self.get_context_data(choices=choices, tested_entry=tested_entry)
        )

    def post(self, request, *args, **kwargs):
        entry_id = request.POST['tested_entry_id']
        answer_correct = entry_id == request.POST.get('chosen_entry_id')

        record = KanjiTestingRecord.objects.get(
            kanji_entry_id=entry_id,
            user_id=request.user.id
        )

        if answer_correct:
            interval = (
                DEFAULT_BASE_INTERVAL *
                math.pow(DEFAULT_INTERVAL_RATE, record.correct_streak)
            )

            record.correct_streak += 1
            record.test_date += timedelta(days=interval)
            record.save()

        elif record.correct_streak != 0:
            record.correct_streak = 0
            record.test_date = date.today()
            record.save()

        return HttpResponseRedirect(
            reverse_lazy(
                'test_kanji_reveal',
                kwargs={'entry_id': entry_id}
            ) +
            query_string(answer_correct=answer_correct)
        )


class TestKanjiRevealView(TemplateView):
    template_name = 'tutor/test_kanji_reveal.html'

    extra_context = {
        'title': _('Test Kanji Reveal'),
        'next_link': reverse_lazy('test_kanji')
    }

    def get(self, request, *args, **kwargs):
        entry = KanjiEntry.objects.get(pk=kwargs.get('entry_id'))
        answer_correct = bool(request.GET.get('answer_correct'))

        return self.render_to_response(
            self.get_context_data(entry=entry, answer_correct=answer_correct)
        )


class TestKanjiDoneView(TemplateView):
    template_name = 'tutor/test_kanji_done.html'
    extra_context = {'title': _('Test Kanji Done')}
