from .models import Move
from rest_framework import serializers


class MoveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Move
        fields = ['move_id', 'move_name', 'move_type']