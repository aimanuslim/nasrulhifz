from .models import Hifz, QuranMeta, SurahMeta
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ObjectDoesNotExist


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator()],
            }
        }

class HifzListSerializer(serializers.ListSerializer):

    class Meta:
        validators = ()

    def update(self, instance, validated_data):

        hifz_mapping = {(hifz.surah_number, hifz.ayat_number): hifz for hifz in instance}
        data_mapping = {(item['surah_number'], item['ayat_number']): item for item in validated_data}

        return_json = []
        for identifier, data in data_mapping.items():
            hifz = hifz_mapping.get(identifier, None)
            if hifz is None:
                raise ObjectDoesNotExist()
            else:
                return_json.append(self.child.update(hifz, data))

        return return_json



class HifzSerializer(serializers.ModelSerializer):
    hafiz = UserSerializer(
        write_only=True,
        default=serializers.CurrentUserDefault()
    )

    @classmethod
    def many_init(cls, *args, **kwargs):
        # Instantiate the child serializer.
        kwargs['child'] = cls()
        # Instantiate the parent list serializer.
        return HifzListSerializer(*args, **kwargs)

    def update(self, instance, validated_data):
        instance.average_difficulty = validated_data.get('average_difficulty', instance.average_difficulty)
        instance.last_refreshed = validated_data.get('last_refreshed', instance.last_refreshed)
        instance.save()
        return instance

    class Meta:
        model = Hifz
        extra_kwargs = {'juz_number': {'read_only': True}}
        fields = ('hafiz', 'surah_number', 'ayat_number', 'last_refreshed', 'juz_number', 'average_difficulty')
        list_serializer_class = HifzListSerializer
        # seems like validators doesnt check if you are updating objects.
        validators = [
            UniqueTogetherValidator(
                queryset=Hifz.objects.all(),
                fields=('hafiz', 'surah_number', 'ayat_number'),
            )
        ]




class QuranMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuranMeta
        fields = ('surah_number', 'ayat_number', 'ayat_string', 'juz_number')

class SurahMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurahMeta
        fields = ('surah_number', 'name_string', 'surah_ayat_max')