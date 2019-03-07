from datetime import date, timedelta
import math

from django.test import TestCase

from .models import KanjiLearningRecord, KanjiTestingRecord, KanjiEntry
from .views import DEFAULT_BASE_INTERVAL, DEFAULT_INTERVAL_RATE


class LearnKanjiViewTestCase(TestCase):
    fixtures = ['tutor/learn_kanji_view.json']

    def setUp(self):
        self.client.login(username='tester1@kenkyou.com',
                          password='user')

    def test_get(self):
        for i in [3, 4]:
            KanjiLearningRecord.objects.create(kanji_entry_id=i, user_id=1)

        entry = self.client.get('/learn-kanji/').context.get('entry')

        self.assertNotEqual(
            entry.id, 1,
            msg="Selected the entry for wrong user"
        )
        self.assertNotEqual(
            entry.id, 2,
            msg="Selected the entry that is learnt"
        )
        self.assertNotEqual(
            entry.id, 3,
            msg="Selected the entry with wrong order"
        )
        self.assertEqual(
            entry.id, 4,
            msg="Not select the entry to learn"
        )

    def test_get_no_entry(self):
        response = self.client.get('/learn-kanji/')

        self.assertRedirects(
            response, '/learn-kanji/done/',
            msg_prefix="Not redirect when there is no entry to learn"
        )

    def test_post(self):
        KanjiLearningRecord.objects.create(kanji_entry_id=1, user_id=1)
        response = self.client.post('/learn-kanji/', data={'entry_id': 1})

        learning_record = KanjiLearningRecord.objects.get(
            kanji_entry_id=1,
            user_id=1
        )

        self.assertEqual(
            learning_record.is_learnt, True,
            msg="Learnt entry is not recorded"
        )

        testing_record = KanjiTestingRecord.objects.filter(
            kanji_entry_id=1,
            user_id=1
        ).first()

        self.assertIsNotNone(
            testing_record,
            msg="Testing record is not created"
        )
        self.assertRedirects(
            response, '/learn-kanji/', target_status_code=302,
            msg_prefix="Not redirect to learn another entry"
        )


class TestKanjiViewTestCase(TestCase):
    fixtures = ['tutor/test_kanji_view.json']

    def setUp(self):
        self.client.login(username='tester1@kenkyou.com',
                          password='user')

    def test_get(self):
        for i in range(1, 5):
            record = KanjiTestingRecord.objects.get(pk=i)
            record.test_date = date.today()

            if i == 4:
                record.test_date += timedelta(days=1)

            record.save()

        for i in [5, 6]:
            record = KanjiTestingRecord.objects.create(
                kanji_entry_id=i, user_id=1
            )

        record = KanjiTestingRecord.objects.get(pk=4)
        record.test_date = date.today() + timedelta(days=1)
        record.save()

        context = self.client.get('/test-kanji/').context

        self.assertNotEqual(
            context.get('tested_entry').id, 1,
            msg="Selected the entry that is learnt by wrong user"
        )
        self.assertNotEqual(
            context.get('tested_entry').id, 2,
            msg="Selected the entry that is not learnt yet"
        )
        self.assertNotEqual(
            context.get('tested_entry').id, 3,
            msg="Selected the entry for wrong user"
        )
        self.assertNotEqual(
            context.get('tested_entry').id, 4,
            msg="Selected the entry not due to test yet"
        )
        self.assertNotEqual(
            context.get('tested_entry').id, 5,
            msg="Selected the entry with wrong order"
        )
        self.assertEqual(
            context.get('tested_entry').id, 6,
            msg="Not select the entry to test"
        )
        self.assertEqual(
            len(context.get('choices')), 4,
            msg="Number of choices not correct"
        )

    def test_get_no_entry(self):
        for i in range(1, 5):
            record = KanjiTestingRecord.objects.get(pk=i)
            record.test_date = date.today()

            if i == 4:
                record.test_date += timedelta(days=1)

            record.save()

        response = self.client.get('/test-kanji/')

        self.assertRedirects(
            response, '/test-kanji/done/',
            msg_prefix="Not redirect when there is no entry to test"
        )

    def test_post_answer_correct(self):
        KanjiTestingRecord.objects.create(kanji_entry_id=3, user_id=1)

        response = self.client.post(
            '/test-kanji/',
            data={'tested_entry_id': 3,
                  'chosen_entry_id': 3}
        )

        record = KanjiTestingRecord.objects.get(
            kanji_entry_id=3,
            user_id=1
        )

        interval = (
            DEFAULT_BASE_INTERVAL *
            math.pow(DEFAULT_INTERVAL_RATE, 0)
        )

        self.assertEqual(
            record.correct_streak, 1,
            msg="Correct streak is not updated correctly"
        )
        self.assertEqual(
            record.test_date, date.today() + timedelta(days=interval),
            msg="Test date is not updated correctly"
        )
        self.assertRedirects(
            response, '/test-kanji/reveal/3/?answer_correct=True',
            msg_prefix="Not redirect when answer is correct"
        )

    def test_post_answer_not_correct(self):
        KanjiTestingRecord.objects.create(kanji_entry_id=3, user_id=1)

        response = self.client.post(
            '/test-kanji/',
            data={'tested_entry_id': 3,
                  'chosen_entry_id': 1}
        )

        record = KanjiTestingRecord.objects.get(
            kanji_entry_id=3,
            user_id=1
        )

        self.assertEqual(
            record.correct_streak, 0,
            msg="Correct streak is not updated correctly"
        )
        self.assertEqual(
            record.test_date, date.today(),
            msg="Test date is not updated correctly"
        )
        self.assertRedirects(
            response, '/test-kanji/reveal/3/',
            msg_prefix="Not redirect when answer is incorrect"
        )


class TestKanjiRevealViewTestCase(TestCase):
    fixtures = ['tutor/test_kanji_reveal_view.json']

    def test_get_answer_correct(self):
        response = self.client.get(
            '/test-kanji/reveal/1/', {'answer_correct': True}
        )

        entry = response.context.get('entry')
        answer_correct = response.context.get('answer_correct')

        self.assertEqual(
            entry,
            KanjiEntry.objects.get(pk=1),
            msg="Not select the entry to reveal"
        )
        self.assertEqual(
            answer_correct, True,
            msg="Shown wrong result of answer as correct"
        )

    def test_get_answer_incorrect(self):
        response = self.client.get('/test-kanji/reveal/1/')

        entry = response.context.get('entry')
        answer_correct = response.context.get('answer_correct')

        self.assertEqual(
            entry,
            KanjiEntry.objects.get(pk=1),
            msg="Not select the entry to reveal"
        )
        self.assertEqual(
            answer_correct, False,
            msg="Shown wrong result of answer as incorrect"
        )
