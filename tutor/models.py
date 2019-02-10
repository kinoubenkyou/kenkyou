from django.db import models

from security.models import User


class KanjiEntry(models.Model):
    writing = models.CharField(max_length=1, unique=True)
    on_reading = models.CharField(max_length=100, blank=True)
    kun_reading = models.CharField(max_length=100, blank=True)
    meaning = models.CharField(max_length=100, unique=True)
    order = models.IntegerField()


class KanjiLearningRecord(models.Model):
    kanji_entry = models.ForeignKey(KanjiEntry, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_learnt = models.BooleanField(default=False)


class KanjiTestingRecord(models.Model):
    kanji_entry = models.ForeignKey(KanjiEntry, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_date = models.DateField(auto_now_add=True)
    correct_streak = models.IntegerField(default=0)
