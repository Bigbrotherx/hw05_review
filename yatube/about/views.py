from django.views.generic.base import TemplateView


class AboutAuthorsView(TemplateView):
    template_name: str = 'about/author.html'


class AboutTechView(TemplateView):
    template_name: str = 'about/tech.html'
