from django.contrib import admin
from .models import Brand, CarModel, BodyType, Configuration, Car

admin.site.register(Brand)
admin.site.register(CarModel)
admin.site.register(BodyType)
admin.site.register(Configuration)
admin.site.register(Car)