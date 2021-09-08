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
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
 
import pyotp
from twilio.rest import Client as TwilioClient
from decouple import config

from .serializers import UserSerializer, EditUserSerializer, GetUserSerializer
from .models import CustomUserModel
import api.signals

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


	def get_serializer_class(self):

		if self.request.method == 'GET':
			return GetUserSerializer
		elif self.request.method == 'PATCH':
			return EditUserSerializer

		return self.serializer_class



class CreateUser(generics.CreateAPIView):

	serializer_class = UserSerializer




class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):

    	sms_code = request.data['password']
    	code = sms_code
    	get_phone = request.data['username']
    	user = CustomUserModel.objects.get(phone=get_phone)
    	print(code)
    	if user.authenticate(code):
    		password = CustomUserModel.objects.make_random_password(length=20, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+<>~-_,")
    		user.is_active = True
    		user.set_password(password)
    		user.save()
    		serializer = self.serializer_class(data={'username': get_phone, 'password': password},
    			context={'request': request})
    		serializer.is_valid(raise_exception=True)
    		user = serializer.validated_data['user']
    		token, created = Token.objects.get_or_create(user=user)
    		return Response({'token': token.key})
    	else:
    		action = 'Not verified'
    		return Response({'message': 'otp not verified'}, status=400)



@api_view(['POST'])
def send_sms_code(request, format=None):

	if request.method == "POST":
		try:
			action = ''
			num = request.data['phone']
			user = CustomUserModel.objects.get(phone=num)
			#Time based otp
			time_otp = pyotp.TOTP(user.key, interval=200)
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

			action = 'Login'
			return Response({'message': 'otp sent', 'action': action}, status=200)

		except CustomUserModel.DoesNotExist:
			user = CustomUserModel.objects.create(phone=num)
			password = CustomUserModel.objects.make_random_password(length=20, allowed_chars="abcdefghjkmnpqrstuvwxyz01234567889ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+<>~-_,")
			user.set_password(password)
			user.is_active = False
			user.save()

			#Time based otp
			time_otp = pyotp.TOTP(user.key, interval=200)
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

			action = 'create'
			return Response({'message': 'otp sent', 'action': action}, status=200)




@api_view(['POST'])
def verify_phone(request, sms_code, format=None):

	try:

		code = int(sms_code)
		get_phone = request.data['phone']
		user = CustomUserModel.objects.get(phone=get_phone)

		if not user.authenticate(code):
			user.is_active = True
			user.set_password(code)
			user.save()

			return Response({'message': 'User Verified'}, status=201)

		else:
			user.is_active = False
			user.save()
			return Response(dict(detail='The provided code did not match or has expired'), status=400)

	except:

		return Response(dict(detail='Invalid OTP'), status=404)



@api_view(['POST'])
def reset_pass(request):

	if request.method == "POST":

		try:
			get_num = request.data['phone']
			user = CustomUserModel.objects.get(phone=get_num)

			if user.is_active:

				time_otp = pyotp.TOTP(user.key, interval=300)
				time_otp = time_otp.now()
				#Phone number must be international and start with a plus '+'   
				user_phone_number = user.phone
				user_phone_number = '+91' + user.phone
				client.messages.create(
					body="Your verification code is "+time_otp,
					from_=twilio_phone,
					to=user_phone_number
				)


				return Response({'message': 'otp sent'}, status=200)

			else:
				return Response(dict(detail="Looks like you already have an account, but you haven't verified your phone number"), status=401)

		except CustomUserModel.DoesNotExist:

			return Response(dict(detail="There's no account associated with this number. Please create an account now!"), status=404)






@api_view(['POST'])
def reset_pass_verify(request, reset_sms, format=None):

	try:

		code = int(reset_sms)
		get_num = request.data['phone']
		user = CustomUserModel.objects.get(phone=get_num)

		if request.method == 'POST' and user.authenticate(code):
			
			return Response({'message': 'User Verified'}, status=200)

		return Response(dict(detail='The provided code did not match or has expired'),status=401)

	except:

		return Response(dict(detail='Please enter a valid OTP'), status=406)



@api_view(['PATCH'])
def resetPass(request):

	if request.method == 'PATCH':
		 phone = request.data['phone']
		 password = request.data['password']

		 user = CustomUserModel.objects.get(phone=phone)

		 user.set_password(password)
		 user.save()

		 return Response(dict(detail='Password successfully updated'), status=200)