from django.contrib import admin
from Apps.encuestador.models import Item
from Apps.encuestador.models import ItemClassification
# Register your models here.

admin.site.register(Item)


class ItemClassificationAdmin(admin.ModelAdmin):
    fields = ('name', 'type')
admin.site.register(ItemClassification, ItemClassificationAdmin)