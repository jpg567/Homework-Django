from django.contrib import admin
from .models import Homework, HomeworkPicture

class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('id', 'score', 'score_created_at', 'week_number', 'created_at')  # Adjust fields as necessary
class HomeworkPictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'homework', 'image', 'created_at')  # Adjust fields as necessary


admin.site.register(Homework, HomeworkAdmin)
admin.site.register(HomeworkPicture, HomeworkPictureAdmin)