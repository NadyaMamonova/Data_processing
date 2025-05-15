from django.contrib import admin

from .models import BodyType, Brand, Car, CarModel, Configuration


admin.site.register(Brand)
admin.site.register(CarModel)
admin.site.register(BodyType)
admin.site.register(Configuration)
admin.site.register(Car)


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'object_id', 'action', 'timestamp']
    list_filter = ['action', 'model_name']
    readonly_fields = ['model_name', 'object_id', 'action', 'changes', 'user', 'timestamp']
    show_full_result_count = False
    list_per_page = 50