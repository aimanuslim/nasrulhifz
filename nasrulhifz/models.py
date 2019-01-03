import datetime
from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _
from nasrulhifz.helper import get_appropriate_timeunits_from_day
from django.contrib.auth.models import User

class DifficultyChoice(Enum):   # A subclass of Enum
    EASY = 3
    MEDIUM = 2
    HARD = 1

# Create your models here.
class Hifz(models.Model):
    hafiz = models.ForeignKey(User, on_delete=models.CASCADE)
    surah_number = models.SmallIntegerField()
    ayat_number = models.SmallIntegerField()
    last_refreshed = models.DateField(_("Date"), default=datetime.date.today)
    juz_number = models.SmallIntegerField(blank=True)
    average_difficulty = models.SmallIntegerField()


    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.juz_number is None:
            self.find_juz_number()
        super(Hifz, self).save()

    def __str__(self):
        return "Surah number {} ayat number {} Last Refreshed on {} user {}".format(self.surah_number, self.ayat_number, self.last_refreshed, self.hafiz)

    def save_average_difficulty(self):
        wset = self.wordindex_set.all()
        self.average_difficulty = sum(w.difficulty  for w in wset) / len(wset)

    def get_last_refreshed_timelength(self):
        now = datetime.date.today()
        diff = now - self.last_refreshed
        string = get_appropriate_timeunits_from_day(diff.days) + " ago"
        return string

    def get_number_of_days_since_refreshed(self):
        now = datetime.date.today()
        diff = now - self.last_refreshed
        return diff.days
    def get_hifz_average_difficulty(self):
        # if not self.average_difficulty:
        #     wset = self.wordindex_set.all()
        #     return sum(w.difficulty  for w in wset) / len(wset)
        # else:
        return self.average_difficulty

    def find_juz_number(self):
        if self.surah_number is not None and self.ayat_number is not None:
            res  =  QuranMeta.objects.get(surah_number=self.surah_number, ayat_number=self.ayat_number)
            self.juz_number = res.juz_number + 1





class WordIndex(models.Model):
    hifz = models.ForeignKey(Hifz, on_delete=models.CASCADE)
    index = models.SmallIntegerField()
    difficulty = models.SmallIntegerField(choices=[(tag, tag.value) for tag in DifficultyChoice])

    def __str__(self):
        return "Index {}".format(self.index)


class QuranMeta(models.Model):
    surah_number = models.SmallIntegerField()
    ayat_number = models.SmallIntegerField()
    ayat_string = models.CharField(max_length=10000)
    juz_number = models.SmallIntegerField()


class SurahMeta(models.Model):
    surah_number = models.SmallIntegerField()
    name_string = models.CharField(max_length=100)
    surah_ayat_max = models.SmallIntegerField()