from django.db import models
from enum import Enum

class DifficultyChoice(Enum):   # A subclass of Enum
    EASY = 3
    MEDIUM = 2
    HARD = 1

# Create your models here.
class Hifz(models.Model):
    surah_number = models.SmallIntegerField()
    ayat_number = models.SmallIntegerField()

    def __str__(self):
        return "Surah number {} ayat number {}".format(self.surah_number, self.ayat_number)

class WordIndex(models.Model):
    hifz = models.ForeignKey(Hifz, on_delete=models.CASCADE)
    index = models.SmallIntegerField()
    difficulty = models.SmallIntegerField(choices=[(tag, tag.value) for tag in DifficultyChoice])

    def __str__(self):
        return "Index {}".format(self.index)


class QuranMeta(models.Model):
    surah_number = models.CharField(max_length=10000)
    ayat_number = models.CharField(max_length=10000)
    ayat_string = models.CharField(max_length=10000)


class SurahMeta(models.Model):
    surah_number = models.SmallIntegerField()
    name_string = models.CharField(max_length=100)
    surah_ayat_max = models.SmallIntegerField()