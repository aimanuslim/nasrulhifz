from django.db import models

# Create your models here.
class Hifz(models.Model):
	surah_number = models.SmallIntegerField()	
	ayat_number = models.SmallIntegerField()

	def __str__(self):
		return "Surah number {} ayat number {}".format(self.surah_number, self.ayat_number)

class WordIndex(models.Model):
	hifz = models.ForeignKey(Hifz, on_delete=models.CASCADE)
	index = models.SmallIntegerField()

	def __str__(self):
		return "Index {}".format(self.index)



class QuranMeta(models.Model):
	surah_number = models.SmallIntegerField()
	ayat_number = models.SmallIntegerField()
	ayat_string = models.CharField(max_length=100000)