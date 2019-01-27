from django.urls import path

from . import views


urlpatterns = [
    path('learn-kanji/', views.LearnKanjiView.as_view(), name='learn_kanji'),
    path('learn-kanji/done', views.LearnKanjiDoneView.as_view(),
         name='learn_kanji_done')
]
