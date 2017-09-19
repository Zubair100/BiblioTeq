from django.contrib.auth.models import User
from rest_framework import serializers


def jwt_response_payload_handler(token, user=None, request=None):
    assert user is not None
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', )