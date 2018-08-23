import datetime
from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _
from qurandata.helper import get_appropriate_timeunits_from_day
from django.contrib.auth.models import User

class DifficultyChoice(Enum):   # A subclass of Enum
    EASY = 3
    MEDIUM = 2
    HARD = 1

# Create your models here.
class Hifz(models.Model):
    hafiz = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    surah_number = models.SmallIntegerField()
    ayat_number = models.SmallIntegerField()
    last_refreshed = models.DateField(_("Date"), default=datetime.date.today)



    def __str__(self):
        return "Surah number {} ayat number {} Last Refreshed on {} user {}".format(self.surah_number, self.ayat_number, self.last_refreshed, self.hafiz)

    def get_last_refreshed_timelength(self):
        now = datetime.date.today()
        diff = now - self.last_refreshed
        string = get_appropriate_timeunits_from_day(diff.days) + " ago"
        return string



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
    juz_number = models.SmallIntegerField()


class SurahMeta(models.Model):
    surah_number = models.SmallIntegerField()
    name_string = models.CharField(max_length=100)
    surah_ayat_max = models.SmallIntegerField()