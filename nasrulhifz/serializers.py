from .models import Hifz, QuranMeta, SurahMeta
from rest_framework import serializers
from rest_framework.serializers import as_serializer_error
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.exceptions import NotFound
from rest_framework.fields import empty
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate
import re
from email.utils import parseaddr

def emailValid(email):
    rettuples = parseaddr(email)
    if len(rettuples[1]) > 0:
            return True
    return False


class AuthCustomTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            if not emailValid(email): 
                msg = 'Email format invalid.'
                raise ValidationError(msg)
            else:
                user = authenticate(username=email, password=password)
                
        else:
            msg = 'Email and/or password parameters missing'
            raise ValidationError(msg)
    
        attrs['user'] = user
        return attrs
        
            


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['email'],
            email=validated_data['email']
        )


        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('id', 'email','password')
        
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {
                'validators': [
                    #Note: uniquevalidator is causing multiple updates to fail. So neeed to remove this.
                    # Even without uniquevalidator, registering a user with same username in database will fail, so we dont really need to include this uniquevalidator then.
                    # UniqueValidator(
                    #     queryset=User.objects.all(),
                    #     message="Username already registered. Please select a new one."),
                    ],
            },
            'email': {
                'validators': [
                ]
            }
        }

class HifzListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):

        hifz_mapping = {(hifz.surah_number, hifz.ayat_number): hifz for hifz in instance}
        data_mapping = {(item['surah_number'], item['ayat_number']): item for item in validated_data}

        return_json = []
        for identifier, data in data_mapping.items():
            hifz = hifz_mapping.get(identifier, None)
            if hifz is None:
                raise NotFound('Hifz specified do not exists.')
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
        instance.revised_count = validated_data.get('revised_count', instance.revised_count)
        instance.save()
        return instance

    class Meta:
        model = Hifz
        extra_kwargs = {'juz_number': {'read_only': True}}
        fields = ('hafiz', 'surah_number', 'ayat_number', 'last_refreshed', 'juz_number', 'average_difficulty', 'revised_count')
        list_serializer_class = HifzListSerializer
        # seems like validators doesnt check if you are updating objects.
        validators = [
            UniqueTogetherValidator(
                queryset=Hifz.objects.all(),
                fields=('hafiz', 'surah_number', 'ayat_number'),
                message='Hifz trying to be created must not already exist.'
            )
        ]








class QuranMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuranMeta
        fields = ('surah_number', 'ayat_number', 'ayat_string', 'juz_number')
        # list_serializer_class = QuranMetaListSerializer
        depth = 2

class QuranMetaListSerializer(serializers.Serializer):
    data = serializers.ListField(child=QuranMetaSerializer())
    fields='__all__'



class SurahMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurahMeta
        fields = ('surah_number', 'name_string', 'surah_ayat_max')