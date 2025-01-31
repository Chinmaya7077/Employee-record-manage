# from django.contrib import admin
# from taskapp.models import task,Technology


# class taskadmin(admin.ModelAdmin):
#     list_display=['first_name','last_name','mail_id','technology','salary']


# admin.site.register(task,taskadmin)
# admin.site.register(Technology)

# # Register your models here.


from django.contrib import admin
from taskapp.models import task, Technology


class TaskAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'mail_id', 'get_technologies', 'salary']

    # Custom method to display technologies
    def get_technologies(self, obj):
        return ", ".join([tech.name for tech in obj.technology.all()])
    
    get_technologies.short_description = "Technologies"  # Column header in the admin panel


admin.site.register(task, TaskAdmin)
admin.site.register(Technology)
