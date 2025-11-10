from django.urls import path
from .views import vton_demo, vton_tryon_api

urlpatterns = [
    path("demo/", vton_demo, name="vton_demo"),
    path("tryon_api/", vton_tryon_api, name="tryon_api"),
]
