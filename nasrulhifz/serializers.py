from .models import Hifz, QuranMeta
from rest_framework import serializers


class HifzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hifz
        fields = ('surah_number', 'ayat_number', 'last_refreshed', 'juz_number', 'average_difficulty')