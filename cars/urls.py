from django.urls import path
from .views import AddCarsFromXML, StatisticsView

urlpatterns = [
    path('add/', AddCarsFromXML.as_view(), name='add_cars'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
]
