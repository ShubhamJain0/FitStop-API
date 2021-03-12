from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from rest_framework import viewsets, status, generics, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
 
import pyotp
from twilio.rest import Client as TwilioClient
from decouple import config

from .serializers import UserSerializer, EditUserSerializer
from .models import CustomUserModel, InactiveUserId, ResetPassUserId


# Create your views here.

account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_phone = config("TWILIO_PHONE")
client = TwilioClient(account_sid, auth_token)


User = get_user_model()


def first(request):

	return HttpResponse('Hello there!')


class User(generics.RetrieveUpdateAPIView):

	serializer_class = EditUserSerializer
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated, )

	def get_object(self):

		return self.request.user



class CreateUser(generics.CreateAPIView):

	serializer_class = UserSerializer



@api_view(['POST'])
def send_sms_code(request, format=None):

	if request.method == "POST":
		try:
			num = request.data['phone']
			user = CustomUserModel.objects.get(phone=num)
			#Time based otp
			time_otp = pyotp.TOTP(user.key, interval=300)
			time_otp = time_otp.now()
			#Phone number must be international and start with a plus '+'  
			user_phone_number = '+91' + user.phone
			#use_phone_number = '{0:+}'.format(int(user_phone_number))
			#print(use_phone_number)
			client.messages.create(
				body="Your verification code is "+time_otp,
				from_=twilio_phone,
				to=user_phone_number
			)

			InactiveUserId.objects.create(id_of_user=user.id, otp_code=time_otp)

			return Response(status=200)
		except CustomUserModel.DoesNotExist:
			return Response({'message': 'User with this number does not exist'}, status=401)




@api_view(['GET'])
def verify_phone(request, sms_code, format=None):

	try:

		code = int(sms_code)
		get_id = InactiveUserId.objects.filter(otp_code=code).values_list('id_of_user', flat=True)
		user = CustomUserModel.objects.get(id__in=get_id)

		if user.authenticate(code):
			user.is_active = True
			user.save()
			InactiveUserId.objects.filter(id_of_user=user.id).delete()

			return Response({'message': 'User Created'}, status=201)

		user.is_active = False
		user.save()
		return Response(dict(detail='The provided code did not match or has expired'),status=200)

	except:

		return Response(dict(detail='Please enter a valid OTP'), status=406)



@api_view(['POST'])
def reset_pass(request):

	if request.method == "POST":

		try:
			get_num = request.data['phone_number']
			user = CustomUserModel.objects.get(phone=get_num)

			if user.is_active:

				time_otp = pyotp.TOTP(user.key, interval=300)
				time_otp = time_otp.now()
				#Phone number must be international and start with a plus '+'   
				user_phone_number = user.phone
				client.messages.create(
					body="Your verification code is "+time_otp,
					from_=twilio_phone,
					to=user_phone_number
				)

				ResetPassUserId.objects.create(reset_user_id=user.id, reset_code=time_otp)

				return Response(status=200)

			else:
				return Response(dict(detail="Looks like you already have an account, but you haven't verified your phone number"), status=401)

		except CustomUserModel.DoesNotExist:

			return Response(dict(detail="There's no account associated with this number. Please create an account now!"), status=404)






@api_view(['GET', 'PUT', 'PATCH'])
def reset_pass_verify(request, reset_sms, format=None):

	try:

		code = int(reset_sms)
		get_id = ResetPassUserId.objects.filter(reset_code=code).values_list('reset_user_id', flat=True)
		user = CustomUserModel.objects.get(id__in=get_id)

		if request.method == 'GET' and user.authenticate(code):

			return Response({'message': 'User Verified'}, status=200)

		if request.method == "PATCH":

			password = request.data['password']
			user.set_password(password)
			user.save()

			ResetPassUserId.objects.filter(reset_user_id=user.id).delete()

			return Response(dict(detail='Password successfully updated'), status=200)

		return Response(dict(detail='The provided code did not match or has expired'),status=401)

	except:

		return Response(dict(detail='Please enter a valid OTP'), status=406)