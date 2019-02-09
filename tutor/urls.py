from django.urls import path

from . import views


urlpatterns = [
    path('learn-kanji/', views.LearnKanjiView.as_view(), name='learn_kanji'),
    path('learn-kanji/done', views.LearnKanjiDoneView.as_view(),
         name='learn_kanji_done'),

    path('test-kanji/', views.TestKanjiView.as_view(), name='test_kanji'),
    path('test-kanji/reveal', views.TestKanjiRevealView.as_view(),
         name='test_kanji_reveal'),
    path('test-kanji/done', views.TestKanjiDoneView.as_view(),
         name='test_kanji_done')
]
