from django.shortcuts import render,redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.contrib import messages
from django.db import connection
from .models import Animes
import numpy as np
import time
import requests
import ast
import os
import json

def input(request):
    try:
        error = request.GET.get('error') 
    except:
        error = "0"
    context = {
            'error': error,
            }
    return render(request,'input.html',context)

def result(request):

    redirect_url = reverse('recommend:input')
    title = request.POST.get('term', False)
    count = request.POST.get('count', '0')
    if not count.isdecimal():
        count = 0
    count = int(count)

    if not title:
        print("------入力されていません------")
        messages.error(request, '何らかのアニメを入力してください')
        return redirect(redirect_url)
    
    print("------タイトルが入力されました------")
    
    if count <= 0 or count > 30:
        messages.error(request, '件数は1~30の間で入力してください')
        return redirect(redirect_url)

    try:
        target_data = Animes.objects.get(title=title)
    except:
        messages.error(request, '入力したアニメがありませんでした')
        return redirect(redirect_url)

    recommend_dict = json.loads(target_data.recommend_list)

    if len(recommend_dict) < count:
        messages.error(request, '入力したアニメがありませんでした')
        return redirect(redirect_url)

    print("------レコメンドリスト作成------")
    recommend_list = []
    for i in range(count): 
        recommend_anime = Animes.objects.get(id=recommend_dict[i]["id"])
        title = recommend_anime.title
        outline = recommend_anime.outline_entire
        similarity = recommend_dict[i]["sim"]
        url = recommend_anime.url
        recommend_anime_info = {
                "title": title,
                "outline": outline,
                "similarity": similarity,
                "url": url,
                "rank": i+1
                }
        recommend_list.append(recommend_anime_info)
    context = {
                'list': recommend_list,
                }
    return render(request,'result.html',context)


# formのautocomplete用メソッド
# 入力された文字列を含むタイトルを返す
def anime_autocomplete(request):
    if request.is_ajax():
        query = request.GET.get("term", "")
        animes = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT title FROM animes WHERE MATCH(title_full) AGAINST(%s) AND recommend_list IS NOT NULL AND is_delivery = 1", [str(query)])
            animes = cursor.fetchall()
        time_1 = time.perf_counter()
        results = []
        for i, anime in enumerate(animes):
            if i > 10:
                break
            time_loop = time.perf_counter()
            title_json = anime[0]
            results.append(title_json)
        data = json.dumps(results)
    mimetype = "application/json"
    return HttpResponse(data, mimetype)


