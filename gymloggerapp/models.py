from django.conf import settings
from django.db import models
import datetime

class MuscleGroup(models.Model):
	'''
	This model is the muscle group.
	'''
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	muscle = models.CharField(max_length=100, default = '')
	delete_true = models.BooleanField(default=False)

	def __str__(self):
		return self.muscle

class ExerciseName(models.Model):
	'''
	This model is an exercise, relating to a muscle group. 
	'''
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	muscle_group = models.ForeignKey(MuscleGroup, on_delete = models.CASCADE)
	name_of_exercise = models.CharField(max_length=100, default = '')
	delete_true = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name_of_exercise


class SetLogger(models.Model):
	'''
	This model is a set, relating to an exercise. 
	'''

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	weight = models.IntegerField(default=0)
	reps = models.IntegerField(default=0)
	date = models.DateField(default=datetime.date.today)
	exercisegroup = models.ForeignKey(ExerciseName, on_delete = models.CASCADE)
	delete_true = models.BooleanField(default=False)

	
	

