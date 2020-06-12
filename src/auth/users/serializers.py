from rest_framework import serializers


class ConfirmRegistrationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=200, required=True)
    password = serializers.CharField(max_length=64, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
