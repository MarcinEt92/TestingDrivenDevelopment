from django.shortcuts import render, redirect
from .models import Item, List


# Create your views here.


def home_page(request):
    return render(request, "home.html")


def new_list(request):
    to_do_list = List.objects.create()
    Item.objects.create(text=request.POST["new_item"], list=to_do_list)
    return redirect(f"/lists/{to_do_list.id}/")


def view_list(request, list_id):
    to_do_list = List.objects.get(id=list_id)
    items = Item.objects.filter(list=to_do_list)
    context = {"items": items, "to_do_list": to_do_list}
    return render(request, "list.html", context)


def add_item(request, list_id):
    to_do_list = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST["new_item"], list=to_do_list)
    return redirect(f"/lists/{to_do_list.id}/")
