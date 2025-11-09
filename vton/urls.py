from django.urls import path
from .views import vton_demo

urlpatterns = [
    path("demo/", vton_demo, name="vton_demo"),
]
