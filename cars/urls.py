from django.urls import path

from .views import APIRootView, AddCarsFromXML, StatisticsView


urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('add/', AddCarsFromXML.as_view(), name='add_cars'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),

]