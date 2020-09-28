import datetime
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import re

from .models import ShortLink

WEBSITE_NAME = "http://127.0.0.1:8000/"

# функция для генерации коротких представлений ссылок
def url_generator():
    return "abcdefghijklmnop"


@csrf_exempt
def home_page(request):
    """
    Метод GET для взаимодействия с UI
    Метод POST для обработки JSON запросов
    """
    if request.method == 'GET':
        return render(request, 'base.html')

    elif request.method == 'POST':
        try:  # достаём полную ссылку в зависимости от того, пришёл запрос по HTTP форме из UI или напрямую через json
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            data = {"full_link": request.POST["full_link"]}
        # создаём полноценный объект и сохраняем в БД
        data["short_link"] = url_generator()
        data["created"] = datetime.datetime.now()
        new_obj = ShortLink.objects.create(full_link=data["full_link"],
                                           short_link=data["short_link"],
                                           created=data["created"])
        new_obj.save()
        # чтобы выводились предыдущие запросы, как в bit.ly, но данные берутся по всей БД
        previous_objects = list()
        for previous_object in list(ShortLink.objects.values()):
            previous_objects.append(previous_object)
        return JsonResponse(data)
    return render(request, 'base.html')


def redirect(request, short_link=''):
    """
    Метод GET для перенаправления по короткой ссылке
    """
    if request.method == "GET":  # запросить изначальную ссылку по короткому представлению
        full_link = ShortLink.objects.get(short_link=short_link).full_link
        if re.search(r"^(\w+://)?www\..*", full_link) is None:
            full_link = "www." + full_link
        if re.search(r"^https?://.*", full_link) is None:
            full_link = "http://" + full_link
        return HttpResponseRedirect(full_link)
