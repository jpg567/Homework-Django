from django.contrib import admin

from users.models import Coaches, Student, User


class CoachesAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'full_name', 'created_at', 'is_staff', 'is_superuser')
    

class StudentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone','course', 'full_name', 'created_at', 'is_staff', 'is_superuser')

admin.site.register(Coaches, CoachesAdmin)
admin.site.register(Student, StudentsAdmin)
admin.site.register(User)

