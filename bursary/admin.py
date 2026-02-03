from django.contrib import admin
from .models import Application, County, Constituency, LevelOfStudy

admin.site.register(Application)
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(LevelOfStudy)
