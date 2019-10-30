from django.contrib import admin

# Register your models here.
from .models import SetLogger, ExerciseName, MuscleGroup

admin.site.register(SetLogger)
admin.site.register(ExerciseName)
admin.site.register(MuscleGroup)
