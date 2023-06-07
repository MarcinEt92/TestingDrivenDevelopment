import unittest

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

# Create your tests here.
from django.urls import resolve

from .models import Item, List
from .views import home_page, view_list, new_list, add_item
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

    def test_new_list_view_can_render_item_from_post_request(self):
        to_do_item_one = self.items_list[0]
        request = HttpRequest()
        request.method = "POST"
        request.POST["new_item"] = to_do_item_one
        new_list(request)
        request.method = "GET"
        response = view_list(request, 1)
        self.assertIn(to_do_item_one, response.content.decode())

    def test_new_list_view_can_save_post_request_and_update_database(self):
        to_do_item_one = self.items_list[0]
        request = HttpRequest()
        request.method = "POST"
        request.POST["new_item"] = to_do_item_one
        new_list(request)
        self.assertEqual(Item.objects.first().text, to_do_item_one)
        self.assertEqual(Item.objects.count(), 1)

    def test_redirect_after_post_request(self):
        to_do_item_one = self.items_list[0]
        request = HttpRequest()
        request.method = "POST"
        request.POST["new_item"] = to_do_item_one
        response = new_list(request)
        created_list = List.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get("location"), f"/lists/{created_list.id}/")

    def test_new_list_view_returns_correct_html_after_post(self):
        # create new list
        request = HttpRequest()
        request.method = "POST"
        request.POST["new_item"] = self.items_list[0]
        new_list(request)

        created_list = List.objects.first()

        # add items to created list
        for item in self.items_list[1:]:
            request.method = "POST"
            request.POST["new_item"] = item
            add_item(request, created_list.id)

        request.method = "GET"
        response = view_list(request, created_list.id)
        regex_pattern = '<input type="hidden".*>'
        response_no_hidden_input = re.sub(regex_pattern, repl="", string=response.content.decode())
        context = {"items": Item.objects.all(), "to_do_list": created_list}
        expected_html = render_to_string("list.html", context)
        self.assertEqual(response_no_hidden_input, expected_html)

    def test_view_list_view_displays_more_than_one_item(self):
        to_do_list = List.objects.create()
        for item in self.items_list:
            Item.objects.create(text=item, list=to_do_list)

        request = HttpRequest()
        request.method = "GET"
        response = view_list(request, to_do_list.id)

        for item in self.items_list:
            self.assertIn(item, response.content.decode())


class ItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        to_do_list = List.objects.create()
        items_list = [
            "Absolutely first element from the list",
            "Second element from the list"
        ]
        for item in items_list:
            Item.objects.create(text=item, list=to_do_list)

        saved_items = Item.objects.all()

        self.assertEqual(saved_items.count(), len(items_list))
        for i in range(0, len(items_list)):
            self.assertEqual(saved_items[i].text, items_list[i])


class ListViewTest(TestCase):
    def test_displays_all_items(self):
        to_do_list = List.objects.create()
        item_1 = "Item 1"
        item_2 = "Item 2"
        Item.objects.create(text=item_1, list=to_do_list)
        Item.objects.create(text=item_2, list=to_do_list)

        response = self.client.get(f'/lists/{to_do_list.id}/')

        self.assertContains(response, item_1)
        self.assertContains(response, item_2)

    def test_uses_list_template(self):
        list_created = List.objects.create()
        response = self.client.get(f"/lists/{list_created.id}/")
        list_template_name = "list.html"
        self.assertTemplateUsed(response, list_template_name)

    def test_displays_only_items_for_that_list(self):
        to_do_list = List.objects.create()
        Item.objects.create(text=SmokeTest.items_list[0], list=to_do_list)
        Item.objects.create(text=SmokeTest.items_list[1], list=to_do_list)
        other_to_do_list = List.objects.create()
        other_item_1, other_item_2 = "Item 1", "Item 2"
        Item.objects.create(text=other_item_1, list=other_to_do_list)
        Item.objects.create(text=other_item_2, list=other_to_do_list)

        response = self.client.get(f"/lists/{to_do_list.id}/")

        self.assertContains(response, SmokeTest.items_list[0])
        self.assertContains(response, SmokeTest.items_list[1])
        self.assertNotContains(response, other_item_1)
        self.assertNotContains(response, other_item_2)


class NewListTest(TestCase):
    def test_save_post_request(self):
        self.client.post(
            path="/lists/new",
            data={"new_item": SmokeTest.items_list[0]}
        )
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, SmokeTest.items_list[0])
        self.assertEqual(Item.objects.count(), 1)

    def test_redirects_after_post(self):
        response = self.client.post(
            path="/lists/new",
            data={"new_item": SmokeTest.items_list[0]}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/lists/1/')


class ListAndItemModelsTest(TestCase):
    def test_save_and_retrieve_items(self):
        to_do_list = List()
        to_do_list.save()

        first_item = Item()
        first_item.text = "1st element"
        first_item.list = to_do_list
        first_item.save()

        second_item = Item()
        second_item.text = "2nd element"
        second_item.list = to_do_list
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, to_do_list)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        fist_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(fist_saved_item.text, "1st element")
        self.assertEqual(fist_saved_item.list, to_do_list)
        self.assertEqual(second_saved_item.text, "2nd element")
        self.assertEqual(second_saved_item.list, to_do_list)


if __name__ == '__main__':
    unittest.main()
