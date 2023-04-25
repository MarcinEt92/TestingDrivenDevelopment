import unittest

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

# Create your tests here.
from django.urls import resolve

from .models import Item
from .views import home_page, view_list
import re


class SmokeTest(TestCase):
    items_list = [
        "Buy peacock feather",
        "Use peacock feather to make a bite"
    ]

    def test_bad_maths(self):
        self.assertEqual(1 + 1, 2)

    # resolve() is being used for url analysis and check to which views function url should be mapped to
    def test_root_url_resolves_to_home_page_view(self):
        root_view_name = home_page
        root_resolver = resolve("/")
        self.assertEqual(root_resolver.func, root_view_name)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string("home.html")
        regex_pattern = '<input type="hidden".*>'
        response_no_hidden_input = re.sub(regex_pattern, repl="", string=response.content.decode())
        self.assertEqual(response_no_hidden_input, expected_html)

    def test_does_not_save_items_in_database_using_get_request(self):
        request = HttpRequest()
        request.method = "GET"
        home_page(request)
        self.assertEqual(Item.objects.count(), 0)

    # test not valid after redirect
    def test_home_page_can_render_item_from_post_request(self):
        to_do_item_one = self.items_list[0]
        request = HttpRequest()
        request.method = "POST"
        request.POST["new_item"] = to_do_item_one
        home_page(request)

        request.method = "GET"
        response = view_list(request)
        self.assertIn(to_do_item_one, response.content.decode())

    def test_home_page_can_save_post_request_and_update_database(self):
        to_do_item_one = self.items_list[0]
        request = HttpRequest()
        request.method = "POST"
        request.POST["new_item"] = to_do_item_one
        home_page(request)
        self.assertEqual(Item.objects.first().text, to_do_item_one)
        self.assertEqual(Item.objects.count(), 1)

    def test_redirect_after_post_request(self):
        to_do_item_one = self.items_list[0]
        request = HttpRequest()
        request.method = "POST"
        request.POST["new_item"] = to_do_item_one
        response = home_page(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get("location"), "/lists/the-only-list-in-the-world/")

    def test_home_page_returns_correct_html_after_post(self):
        request = HttpRequest()
        for item in self.items_list:
            request.method = "POST"
            request.POST["new_item"] = item
            home_page(request)

        request.method = "GET"
        response = home_page(request)
        regex_pattern = '<input type="hidden".*>'
        response_no_hidden_input = re.sub(regex_pattern, repl="", string=response.content.decode())
        context = {"items": Item.objects.all()}
        expected_html = render_to_string("home.html", context)
        self.assertEqual(response_no_hidden_input, expected_html)

    def test_home_page_displays_more_than_one_item(self):
        for item in self.items_list:
            Item.objects.create(text=item)

        request = HttpRequest()
        request.method = "GET"
        response = view_list(request)

        for item in self.items_list:
            self.assertIn(item, response.content.decode())


class ItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        items_list = [
            "Absolutely first element from the list",
            "Second element from the list"
        ]
        for item in items_list:
            Item.objects.create(text=item)

        saved_items = Item.objects.all()

        self.assertEqual(saved_items.count(), len(items_list))
        for i in range(0, len(items_list)):
            self.assertEqual(saved_items[i].text, items_list[i])


class ListViewTest(TestCase):
    def test_displays_all_items(self):
        item_1 = "Item 1"
        item_2 = "Item 2"
        Item.objects.create(text=item_1)
        Item.objects.create(text=item_2)

        response = self.client.get('/lists/the-only-list-in-the-world/')

        self.assertContains(response, item_1)
        self.assertContains(response, item_2)

    def test_uses_list_template(self):
        response = self.client.get("/lists/the-only-list-in-the-world/")
        list_template_name = "list.html"
        self.assertTemplateUsed(response, list_template_name)


if __name__ == '__main__':
    unittest.main()
