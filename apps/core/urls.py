from django.urls import path

from .views import KitchenSinkView

app_name = "core"

urlpatterns = [path("_design/", KitchenSinkView.as_view(), name="kitchen-sink")]
