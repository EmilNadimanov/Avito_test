import datetime
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from random import choices
import re

from .models import ShortLink

ALPHABET = [char for char in
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"] # массив из символов a-zA-Z0-9
WEBSITE_NAME = "http://127.0.0.1:8000/"

# функция для генерации коротких представлений ссылок
# вариант с простеньким рандомизатором альфавитно-циферной последовательности
# По сути это размещение из 62 по 8 с повторениями, вероятных комбинаций 62^8=218.340.105.584.896 - это 218+ триллионов
# Можно было бы сделать похитрее, например, рассчитывать хэш SHA256, декодировать в ASCII и брать срез, но я не заметил
# преимуществ такого способа, принимая во внимание, что в задании не уделяется внимание безопасности, а псевдорандом
# показывает себя неплохо
def url_generator():
    random_sequence = choices(ALPHABET, k=8)
    return WEBSITE_NAME + ''.join(random_sequence)


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

        # Цикл, чтобы вывести предыдущие запросы, как в bit.ly, но данные берутся по всей БД
        data = []
        for previous_object in list(ShortLink.objects.values("full_link", "short_link", "created")):
            data.append(previous_object)
        return JsonResponse(data, safe=False)
    return render(request, 'base.html')


def redirect(request, short_link=''):
    """
    Метод GET для перенаправления по короткой ссылке
    """
    if request.method == "GET":  # запросить изначальную ссылку по короткому представлению
        full_link = ShortLink.objects.get(short_link=WEBSITE_NAME + short_link).full_link
        if re.search(r"^(\w+://)?www\..*", full_link) is None:
            full_link = "www." + full_link
        if re.search(r"^https?://.*", full_link) is None:
            full_link = "http://" + full_link
        return HttpResponseRedirect(full_link)
