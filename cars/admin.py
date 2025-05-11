from django.contrib import admin

from .models import BodyType, Brand, Car, CarModel, Configuration


admin.site.register(Brand)
admin.site.register(CarModel)
admin.site.register(BodyType)
admin.site.register(Configuration)
admin.site.register(Car)