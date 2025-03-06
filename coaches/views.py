from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from coaches.forms import LoginForm
from coaches.serializers import CoachesSerializer, StudentSerializer
from config.decorators import IsCoach
from homeworks.models import Homework, HomeworkPicture
from users.models import Coaches, Student, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
import random
from decouple import config
from kavenegar import KavenegarAPI, APIException, HTTPException
from django.contrib.auth.hashers import check_password
from django.utils import timezone


def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        verification_code = request.POST.get('verification_code')
        user = Coaches.objects.get(phone=phone)  
        print(user)

        # Check if the verification code is provided
        if verification_code:
            # Validate the verification code
            print(verification_code,user.password,check_password(verification_code, user.password))
            if check_password(verification_code, user.password) :
                user = authenticate(request, phone=phone, password=verification_code)
                if user is not None:
                    login(request, user)
                    return redirect('home')  # Redirect to home after successful login
            else:
                error = 'Invalid phone number or verification code.'
                return render(request, 'apolonYar/auth.html', {'error': error})

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

            return render(request, 'apolonYar/auth.html', {'phone': phone})

    return render(request, 'apolonYar/auth.html')

def logout_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to access this page.")
    else:
        logout(request)
        return redirect('auth')

@login_required(login_url='auth/')
def apolon_yar_home(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to access this page.")
    else:
        apolon_yar = request.user
        students = Student.objects.all()
        homeworks = Homework.objects.all()
        green_status = True
        for homework in homeworks:
            if homework.created_at < homework.score_created_at:
                green_status = False
            print('create',homework.created_at)
            print('score',homework.score_created_at)
            # homework_pics = HomeworkPicture.objects.filter(homework = homework)
            # print(homework_pics)
        return render(request, 'apolonYar/index.html', {
            "apolonYar": apolon_yar,
            "students": students,
            "homeworks": homeworks,
            "green_status": green_status,
            })

def studentHomeworkRender(request, id, week_number):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to access this page.")
    else:
        student = get_object_or_404(Student, id=id)
        homework = get_object_or_404(Homework, student=student, week_number=week_number)
        
        # Use filter to get all pictures related to the homework
        pictures = HomeworkPicture.objects.filter(homework=homework)
        
        return render(request, 'apolonYar/student-homeWorks.html', {
            'student': student,
            'homework': homework,
            'pictures': pictures,
        })

class SubmitScoreView(APIView):
    permission_classes = [IsCoach]
    def post(self, request):
        # Use request.data to get the data sent in the request
        score = request.data.get('score')
        homework_id = request.data.get('homework_id')  # Assuming you pass the homework ID
        if not score or not homework_id:
            return JsonResponse({"message": "Score and homework ID are required!"}, status=400)

        try:
            homework = Homework.objects.get(id=homework_id)
            homework.score = score  # Update the score
            homework.score_created_at = timezone.now()
            homework.save()
            return JsonResponse({"message": "Score submitted successfully!", "homework_id": homework_id, "score": score}, status=200)
        except Homework.DoesNotExist:
            return JsonResponse({"message": "Homework not found!"}, status=404)
        
class ApolonYarCreateAPIView(APIView):
    permission_classes = [IsCoach]
    def post(self, request):
        serializer = CoachesSerializer(data=request.data)
        if serializer.is_valid():
            verification_code = '12345' 
            coach = Coaches.objects.create_user(
                is_staff = True ,
                phone=serializer.validated_data['phone'],
                verification_code=verification_code,
                full_name=serializer.validated_data['full_name'],
                profile= 'media/profiles/profile.png'
            )
            return Response({"message": "آپولون یار ثبت شد"}, status=status.HTTP_201_CREATED)
        return Response({"message": "آپولون یار ثبت نشد!", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ApolonYarEditAPIView(APIView):
    permission_classes = [IsCoach]

    def put(self, request, id):
        print(request.data)
        try:
            coach = Coaches.objects.get(id=id)
        except Coaches.DoesNotExist:
            return Response({"message": "Coach not found!"}, status=status.HTTP_404_NOT_FOUND)

        # Extract data from the request
        full_name = request.data.get('full_name')
        phone = request.data.get('phone')
        profile = request.FILES.get('profile')
        # Validate the data
        errors = {}
        if User.objects.filter(phone=phone).exists():
            return Response({"message": "یک شماره دیگر وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if len(phone) > 15:
            errors['phone'] = "Phone number must be at most 15 characters."

        if errors:
            return Response({"message": "آپولون یار به روز نشد!", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Update the coach's information
        if full_name:
            coach.full_name = full_name
        if phone:
            coach.phone = phone
        if profile:
            coach.profile = profile
        coach.save()  

        return Response({"message": "آپولون یار به روز شد"}, status=status.HTTP_200_OK)

class StudentCreateAPIView(APIView):
    permission_classes = [IsCoach]
    def post(self, request):
        print(request.data) 
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            verification_code = '12345' 
            student = Student.objects.create_user(
                phone=serializer.validated_data['phone'],
                verification_code=verification_code,
                full_name=serializer.validated_data['full_name'],
                course=serializer.validated_data['course']
            )
            for week_number in range(1, 9):
                Homework.objects.create_homework(
                    student=student,
                    week_number=week_number,
                )
            return Response({"message": "هنرجو ثبت شد"}, status=status.HTTP_201_CREATED)
        return Response({"message": "هنرجو ثبت نشد!", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
