import datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

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
        # парсим входящий джейсон-запрос, сохраняем соответствующий объект в БД и возвращаем джейсон обратно
        data = json.loads(request.body)
        data["short_link"] = url_generator()
        data["created"] = datetime.datetime.now()
        new_obj = ShortLink.objects.create(full_link=data["full_link"],
                                           short_link=data["short_link"],
                                           created=data["created"])
        new_obj.save()
        return JsonResponse(data)
    return render(request, 'base.html')


def redirect(request, short_link=''):
    """
    Метод GET для перенаправления по короткой ссылке
    """
    if request.method == "GET":  # запросить изначальную ссылку по короткому представлению
        pass
