from django.db import models

# Create your models here.
class slackuser(models.Model):
	slackuseID = models.CharField(max_length = 50)
	teamID = models.CharField(max_length = 50)
	real_name = models.CharField(max_length = 500)
	is_admin = models.IntegerField()
	is_owner = models.IntegerField()
	is_primary_owner = models.IntegerField()
	is_restricted = models.IntegerField()
	is_ultra_restricted = models.IntegerField()
	is_deleted = models.IntegerField()
	is_bot = models.IntegerField()

	def __str__(self):
		return self.slackuseID

class dialogflowintent(models.Model):
	intentName = models.CharField(max_length = 1000)
	accuracy = models.FloatField()

	def __str__(self):
		return self.intentName

