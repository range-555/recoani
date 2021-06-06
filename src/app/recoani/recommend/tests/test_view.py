from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse
from recommend.models import Animes


class TestView(TestCase):
    def setUp(self):
        self.lion = Animes.objects.create(id=1, title="lion", outline_entire="lion!", recommend_list="2", doc_vec="1")
        self.cat = Animes.objects.create(id=2, title="cat", outline_entire="cat!", recommend_list="1", doc_vec="1")

    def test_urlview(self):
        result = self.client.post(resolve_url('recommend:input'))
        with self.subTest('レスポンスが正常'):
            self.assertEqual(200, result.status_code)
        with self.subTest('入力画面を表示している'):
            self.assertTemplateUsed(result, 'input.html')

    def test_resultview_valid(self):
        query = {
            'term': 'lion',
            'count': 1
        }
        result = self.client.post(resolve_url('recommend:result'), query)
        with self.subTest('レスポンスが正常'):
            self.assertEqual(200, result.status_code)
        with self.subTest('表示用画面に遷移している'):
            self.assertTemplateUsed(result, 'result.html')
        with self.subTest('タイトルを正しく取得できている'):
            self.assertEqual(result.context['list'][0]['title'], 'cat')
        with self.subTest('あらすじを正しく取得できている'):
            self.assertEqual(result.context['list'][0]['outline'], 'cat!')

    def test_resultview_Invalid(self):
        query = {
            'term': 'test',
        }
        result = self.client.post(resolve_url('recommend:result'), query)
        with self.subTest('入力画面に戻る'):
            self.assertRedirects(result, reverse('recommend:input'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=False)
