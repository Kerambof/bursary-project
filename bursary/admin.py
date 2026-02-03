from django.contrib import admin
from .models import Application, County, Constituency, LevelOfStudy
from django.contrib.auth.models import User

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'admission_number', 'school', 'constituency', 'county', 'level_of_study', 'amount_requested', 'created_at')
    list_filter = ('county', 'constituency', 'level_of_study')
    search_fields = ('full_name', 'admission_number', 'school')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Superuser sees everything
        if request.user.is_superuser:
            return qs
        # If user is a constituency admin, filter to their constituency
        try:
            constituency = Constituency.objects.get(admin=request.user)
            return qs.filter(constituency=constituency)
        except Constituency.DoesNotExist:
            return qs.none()

class ConstituencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'county', 'admin')
    list_filter = ('county',)
    search_fields = ('name', 'county__name', 'admin__username')

admin.site.register(Application, ApplicationAdmin)
admin.site.register(County)
admin.site.register(Constituency, ConstituencyAdmin)
admin.site.register(LevelOfStudy)
