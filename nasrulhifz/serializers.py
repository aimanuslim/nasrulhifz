from .models import Hifz, QuranMeta, SurahMeta
from rest_framework import serializers
from django.contrib.auth.models import User


class HifzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hifz
        extra_kwargs = {'juz_number': {'read_only': True}}
        fields = ('surah_number', 'ayat_number', 'last_refreshed', 'juz_number', 'average_difficulty')


class UserSerializer(serializers.ModelSerializer):
    hifzs = serializers.PrimaryKeyRelatedField(many=True, queryset=Hifz.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'hifz')

class QuranMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuranMeta
        fields = ('surah_number', 'ayat_number', 'ayat_string', 'juz_number')

class SurahMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurahMeta
        fields = ('surah_number', 'name_string', 'surah_ayat_max')