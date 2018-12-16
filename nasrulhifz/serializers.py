from .models import Hifz, QuranMeta
from rest_framework import serializers
from django.contrib.auth.models import User


class HifzSerializer(serializers.ModelSerializer):
    hafiz = serializers.ReadOnlyField(source='hafiz.username')
    class Meta:
        model = Hifz
        fields = ('hafiz', 'surah_number', 'ayat_number', 'last_refreshed', 'juz_number', 'average_difficulty')


class UserSerializer(serializers.ModelSerializer):
    hifzs = serializers.PrimaryKeyRelatedField(many=True, queryset=Hifz.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'hifz')

class QuranMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuranMeta
        fields = ('surah_number', 'ayat_number', 'ayat_string', 'juz_number')