import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt
import json
from random import choices
import re

from .models import ShortLink

ALPHABET = [char for char in
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]  # массив из символов a-zA-Z0-9
WEBSITE_NAME = "http://127.0.0.1:8000/"


# функция для генерации коротких представлений ссылок
# По сути это размещение из 62 по 8 с повторениями, 62^8=218.340.105.584.896 - это 218+ триллионов вероятных комбинаций.
# Можно было бы сделать похитрее, а-ля "взять хэш SHA256 ссылки, преобразовать в человечкочитаемый формат и взять срез
# по первым восьми символам", но, принимая во внимание, что в задании не уделяется внимание безопасности, а псевдорандом
# показал себя неплохо, я остановился на этом. По-хорошему всё должно быть без коллизий
def url_generator():
    random_sequence = choices(ALPHABET, k=8)
    return WEBSITE_NAME + ''.join(random_sequence)


# красивая страничка с историей запросов и преобразований
def query_archive(request):
    # Цикл, чтобы вывести предыдущие запросы, как в bit.ly, но данные берутся по всей БД
    data = []
    for previous_object in list(ShortLink.objects.values("full_link", "short_link", "created")):
        data.append(dict(previous_object))
    return render(request, "query_archive.html", {"data": data})


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
            ui = False
        except json.decoder.JSONDecodeError:
            data = {"full_link": request.POST["full_link"]}
            ui = True
        if data["full_link"] == "":  # проверка на пустой ввод
            return render(request, 'base.html')

        # если во входящем запросе не было "http(s)://www.", то поправим это
        if re.search(r"^(\w+://)?www\..*", data["full_link"]) is None:
            if re.search(r"^([\w\W]+//).*", data["full_link"]) is None:
                data["full_link"] = "www." + data["full_link"]
        if re.search(r"^\w+://.*", data["full_link"]) is None:
            data["full_link"] = "http://" + data["full_link"]

        # создаём полноценный объект и сохраняем в БД
        data["short_link"] = url_generator()
        data["created"] = datetime.datetime.now()
        new_obj = ShortLink.objects.create(full_link=data["full_link"],
                                           short_link=data["short_link"],
                                           created=data["created"])
        new_obj.save()

        # Если запрос приходил по API, то вернём простой джейсон-респонс, в противном случае нарисуем красивую страничку
        if not ui:
            data = []
            # Цикл, чтобы вывести все предыдущие запросы; данные берутся по всей БД
            for previous_object in list(ShortLink.objects.values("full_link", "short_link", "created")):
                data.append(previous_object)
            return JsonResponse(data, safe=False)
        else:  # защита от повторного ввода при обновлении страницы
            return HttpResponseRedirect(reverse("query_archive"))
    # если что-то пришло не по GET и не по POST, то отрисуем страничку заново
    return render(request, 'base.html')


def redirect(request, short_link=''):
    """
    Метод GET для перенаправления по короткой ссылке
    """
    if request.method == "GET":  # запросить изначальную ссылку по короткому представлению
        full_link = ShortLink.objects.get(short_link=WEBSITE_NAME + short_link).full_link

        return HttpResponseRedirect(full_link)  # перенаправить по изначальной ссылке
