from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import CustomUserModel, InactiveUserId
import pyotp
from twilio.rest import Client as TwilioClient
from decouple import config

User = get_user_model()


account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_phone = config("TWILIO_PHONE")
client = TwilioClient(account_sid, auth_token)



class UserSerializer(serializers.ModelSerializer):
	class Meta:

		model = CustomUserModel
		fields = ['phone', 'password']
		extra_kwargs = {'password':{'write_only':True, 'required':True}}


	def create(self, validated_data):

		user = CustomUserModel.objects.create(**validated_data)
		user.set_password(validated_data['password'])
		user.is_active = False
		user.save()

		#Time based otp
		time_otp = pyotp.TOTP(user.key, interval=300)
		time_otp = time_otp.now()
		#Phone number must be international and start with a plus '+'   
		user_phone_number = user.phone
		client.messages.create(
			body="Your verification code is "+time_otp,
			from_=twilio_phone,
			to=user_phone_number
		)

		InactiveUserId.objects.create(id_of_user=user.id, otp_code=time_otp)

		return user






class EditUserSerializer(serializers.ModelSerializer):
	class Meta:

		model = CustomUserModel
		fields = ['email', 'name']


	def update(self, instance, validated_data):
		"""Updates the user, sets password and returns user"""
		password = validated_data.pop('password', None)
		user = super().update(instance, validated_data)

		if password:
			user.set_password(password)
			user.save()

		return user
