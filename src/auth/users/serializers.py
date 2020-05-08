from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=200, required=True)
    password = serializers.CharField(max_length=64, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
