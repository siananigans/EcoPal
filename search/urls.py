from django.urls import path
from . import views
from django.views.generic.base import TemplateView
urlpatterns = [
    path('', views.Find_Coords),
    path('results/', TemplateView.as_view(template_name='results.html')),
    path('results/save/', views.save_search)
]