from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "recommend"
urlpatterns = [
    path('', views.input, name='input'),
    path('result/', views.result, name='result'),
    path('anime-autocomplete/', views.anime_autocomplete, name='anime-autocomplete'),
]

urlpatterns += staticfiles_urlpatterns()
