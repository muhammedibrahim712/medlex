from django.db import models
from django.db import connection
# Create your models here.


class Doc(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return "PDF: %s" % (self.name)


class Tag(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return "Tag: %s" % (self.name)


class Redaction(models.Model):
	str = models.CharField(max_length=120)
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	page = models.IntegerField(default=0)
	state = models.IntegerField(default=0)

	def __str__(self):
		return "Redaction: %s - %s in Page %s" % (self.str, self.tag, self.page)


class Setting(models.Model):
	setting_key = models.CharField(max_length=120)
	setting_value = models.CharField(max_length=120)

	def __str__(self):
		return "Setting: %s - %s" % (self.setting_key, self.setting_value)


class Sentence(models.Model):
	sentence = models.CharField(max_length=999)
	page = models.IntegerField(default=0)
	order = models.IntegerField(default=0)

	def __str__(self):
		return "Sentence: %s in Page %s" % (self.sentence, self.page)