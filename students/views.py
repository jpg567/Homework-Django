from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from config.decorators import IsStudent
from homeworks.models import Homework, HomeworkPicture
from students.serializers import HomeworksSerializer
from users.models import Coaches, Student
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
import random
from decouple import config
from kavenegar import KavenegarAPI, APIException, HTTPException
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse

def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        verification_code = request.POST.get('verification_code')
        user = Student.objects.get(phone=phone)  
        print(user)

        # Check if the verification code is provided
        if verification_code:
            # Validate the verification code
            print(verification_code,user.password,check_password(verification_code, user.password))
            if check_password(verification_code, user.password) :
                user = authenticate(request, phone=phone, password=verification_code)
                if user is not None:
                    login(request, user)
                    return redirect('home-student')  # Redirect to home after successful login
            else:
                error = 'Invalid phone number or verification code.'
                return render(request, 'student/auth.html', {'error': error})

        else:
            code = random.randint(10000, 99999)
            print(user.password)
            user.set_password(str(code)) 
            user.save()
            print(user.password)

            api_key = config('APIKEY')
            try:
                api = KavenegarAPI(api_key)
                params = {
                    'receptor': phone,
                    'token': str(code),
                    'template': 'OTP',
                    'type': 'sms',
                }
                response = api.verify_lookup(params)
                print(response)  # Log the response for debugging

            except APIException as e:
                print(f"API Exception: {e}")
                return JsonResponse({"error": "Failed to send SMS."}, status=500)
            except HTTPException as e:
                print(f"HTTP Exception: {e}")
                return JsonResponse({"error": "HTTP error occurred."}, status=500)

            return render(request, 'student/auth.html', {'phone': phone})

    return render(request, 'student/auth.html')


def logout_view(request):
    if request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to access this page.")
    else:
        logout(request)
        return redirect('login')


@login_required(login_url='login/')
def student_home(request):
    if request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to access this page.")
    else:
        student = request.user
        homeworks = Homework.objects.filter(student=request.user)
        pics_count = 0
        for homework in homeworks:
            print(homework)
            submitted_pictures_count = HomeworkPicture.objects.filter(homework=homework).count()
            print(submitted_pictures_count)
            pics_count += submitted_pictures_count
        print(pics_count)
        max_pictures = 80
        progress_percentage = (pics_count / max_pictures) * 100 if max_pictures > 0 else 0
        return render(request, 'student/index.html', {
            "student": student,
            "homeworks": homeworks,
            "submitted_pictures_count": pics_count,
            "max_pictures": max_pictures,
            "progress_percentage": progress_percentage,
        })

class PicturesSendAPIView(APIView):
    permission_classes = [IsStudent]
    def post(self, request):
        print(request.data)
        week_number = request.data.get('week_number')

        if not week_number:
            return Response({"message": "Week number is required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            homework = Homework.objects.get(week_number=week_number, student=request.user)
        except Homework.DoesNotExist:
            return Response({"message": "Homework for this week does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        if 'pictures' not in request.FILES:
            return Response({"message": "No pictures uploaded!"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the descriptions from the request data
        descriptions = request.data.getlist('descriptions')

        if len(descriptions) != len(request.FILES.getlist('pictures')):
            return Response({"message": "Number of descriptions must match number of pictures!"}, status=status.HTTP_400_BAD_REQUEST)

        for picture, description in zip(request.FILES.getlist('pictures'), descriptions):
            HomeworkPicture.objects.create(
                homework=homework,
                image=picture,
                description=description  # Save the description
            )

        return Response({"message": "Pictures uploaded successfully!"}, status=status.HTTP_201_CREATED)

class PicturesDeleteAPIView(APIView):
    permission_classes = [IsStudent]
    def delete(self, request):
        week_number = request.data.get('week_number')
        picture_urls = request.data.get('pictures', [])  # Expecting URLs now

        if not week_number:
            return Response({"message": "Week number is required!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            homework = Homework.objects.get(week_number=week_number, student=request.user)
        except Homework.DoesNotExist:
            return Response({"message": "Homework for this week does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        if not picture_urls:
            return Response({"message": "No pictures specified for deletion!"}, status=status.HTTP_400_BAD_REQUEST)

        for picture_url in picture_urls:
            # Remove the 'meda/' prefix if it exists
            if picture_url.startswith('/media/'):
                picture_url = picture_url[7:]  # Remove the first 5 characters
            print(picture_url)
            try:
                # Find the HomeworkPicture instance based on the modified image URL
                homework_picture = HomeworkPicture.objects.get(image=picture_url, homework=homework)
                homework_picture.image.delete(save=False)  # Delete the file from the filesystem
                homework_picture.delete()  # Delete the record from the database
            except HomeworkPicture.DoesNotExist:
                continue  # If the picture does not exist, skip it

        return Response({"message": "Pictures deleted successfully!"}, status=status.HTTP_200_OK)

class HomeworkView(APIView):
    permission_classes = [IsStudent]
    def get(self, request):
        week_number = request.query_params.get('week_number')  # Use query_params for GET requests
        try:
            # Fetch the homework for the current student
            homework = Homework.objects.get(week_number=week_number, student=request.user)
            # Fetch all pictures for the homework
            pictures = HomeworkPicture.objects.filter(homework=homework)

            # Prepare a list of picture URLs
            picture_urls = [picture.image.url for picture in pictures]

            return Response({
                'pictures': picture_urls,
                'has_pictures': bool(pictures)
            }, status=status.HTTP_200_OK)

        except Homework.DoesNotExist:
            return Response({'error': 'Homework not found'}, status=status.HTTP_404_NOT_FOUND)