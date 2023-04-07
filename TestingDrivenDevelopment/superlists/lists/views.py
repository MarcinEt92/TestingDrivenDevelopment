from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Item

# Create your views here.


def home_page(request):
    if request.method == "POST":
        new_item = request.POST.get("new_item", "")
        Item.objects.create(text=new_item)
        return redirect("/")

    items = Item.objects.all()
    context = {"items": items}
    return render(request, "home.html", context)
