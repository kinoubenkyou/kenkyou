from django.contrib import admin

from . import models


admin.site.register(models.KanjiEntry)
admin.site.register(models.KanjiLearningRecord)
