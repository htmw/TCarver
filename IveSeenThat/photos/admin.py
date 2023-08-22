from django.contrib import admin

# Register your models here.

from .models import Photo, Category

class PhotoAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    
    
admin.site.register(Category)
admin.site.register(Photo, PhotoAdmin)