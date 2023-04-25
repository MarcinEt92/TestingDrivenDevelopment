from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Item

# Create your views here.


def home_page(request):
    if request.method == "POST":
        new_item = request.POST.get("new_item", "")
        if len(new_item) > 0:
            Item.objects.create(text=new_item)
        return redirect("/lists/the-only-list-in-the-world/")

    return render(request, "home.html")


def view_list(request):
    items = Item.objects.all()
    context = {"items": items}
    return render(request, "list.html", context)
