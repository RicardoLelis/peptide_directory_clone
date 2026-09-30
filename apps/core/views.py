from django.views.generic import TemplateView


class KitchenSinkView(TemplateView):
    template_name = "core/kitchen_sink.html"
