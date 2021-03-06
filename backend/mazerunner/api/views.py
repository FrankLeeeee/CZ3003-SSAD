import statistics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import random

from django.db import IntegrityError
from django.db.models import Avg, Case, Count, Max, Min, Q, TextField, Value, When
from django.http import HttpResponse, JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from gameHistory.models import Section, World, questionHistory
from questions.models import Questions, Questions_answer, Questions_teacher
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

from .forms import signupForm
from .serializers import (LeaderBoardSerializer, LoginSerializer,
                          QuestionHistorySerializer, QuestionStudentSerializer,
                          QuestionTeacherSerializer, StudentAccountSerializer,
                          gameSummarySerializer, overallSummarySerializer)


# TokenAuthentication 
class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []
    def post(self , request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            student = serializer.validated_data
            token, created = Token.objects.get_or_create(user=student)
            return Response({
                "user" : StudentAccountSerializer(student).data,
                "token": token.key
                })
        except:
            return Response({"Error Message" : "Incorrect Email/Password"},status = status.HTTP_401_UNAUTHORIZED)
    


class StudentAPIView(APIView):
    serializer_class = StudentAccountSerializer

    def get_queryset(self):
        users = User.objects.all()
        return users

    def get(self , request):
        try:
            id = request.query_params["id"]
            if id != None:
                student = User.objects.get(id = id)
                serializer = StudentAccountSerializer(student)
        except:
                students = User.objects.filter(is_staff = False)
                serializer = StudentAccountSerializer(students , many = True)    

        return Response(serializer.data)
        
class LeaderBoardAPIView(APIView):
    serializer_class = LeaderBoardSerializer
    def get(self , request):
        students = User.objects.filter(is_staff = False).order_by("-overallScore")
        serializer = LeaderBoardSerializer(students , many = True)
        return Response(serializer.data)

class QuestionAPIView(APIView):
    def post(self , request):
        try:
            world = World.objects.get(name = request.data['world'])
            section = Section.objects.get(name = request.data['section'])

            role = 'no role'
            if(request.data["role"] == "1"):
                role = 'project manager'
            if(request.data["role"] == "2"):
                role = 'frontend'
            if(request.data["role"] == "3"):
                role = 'backend'
            if(int(request.data["questionLevel"])  == 1):
                questions = Questions_teacher.objects.filter(worldID = world , sectionID  = section , role = role, questionLevel = request.data["questionLevel"] ).order_by('?')[:5]   
            else:
                questions = Questions_teacher.objects.filter(worldID = world , sectionID  = section , role = role, questionLevel = request.data["questionLevel"] ).order_by('?')[:3]  
            serializer = QuestionTeacherSerializer(questions , many = True)
            return Response(serializer.data , status = status.HTTP_200_OK)
        except:
            return Response({'Error Message' :'Please enter the correct input'} ,status = status.HTTP_400_BAD_REQUEST)


class QuestionSubmitAPIView(APIView):
    def post(self, request):  
        try: 
            world = World.objects.get(name = request.data['world'])
            section = Section.objects.get(name = request.data['section'])
            point = int(request.data['pointGain'])
            data = {
            "worldID" : world.id,
            "sectionID" : section.id,
            "questionID": request.data['questionID'],
            "studentID" : request.data['studentID'],
            "studentAnswer" : request.data['studentAnswer'],
            "isAnsweredCorrect" : request.data['isAnsweredCorrect'],
            }
            student = User.objects.get(id = request.data['studentID'])
            serializer = QuestionHistorySerializer(data = data)
            if serializer.is_valid() and student!= None:
                serializer.save()
                student.overallScore = student.overallScore + point
                student.save()
                return Response(({'pass': True}) , status = status.HTTP_201_CREATED)
        except:        
            return Response({'pass': False},status = status.HTTP_400_BAD_REQUEST)

class CreateQuestionAPIView(APIView):
    def post(self , request):
        serializer = QuestionStudentSerializer(data = request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response({'submitted': True} , status = status.HTTP_201_CREATED)
        return Response({'submitted':False},status = status.HTTP_400_BAD_REQUEST)

class gameSummaryAPIView(APIView):
    def get(self , request):
        try:
            student = User.objects.get(email = request.data['email'])
            serializer= gameSummarySerializer(student)
            return Response(serializer.data , status = status.HTTP_200_OK)   
        except:
            return Response({'Error Message': 'record not found'} , status = status.HTTP_400_BAD_REQUEST)

class overallSummaryView(APIView):
    """
    View for Dashboard

    Returns:
        HttpResponse: Response that contains all the variables used by dashboard.html template
    """
    authentication_classes = [SessionAuthentication]
    def get(self,request):
        currObjects = dict()
        noParams = True

        if "studentID" in request.query_params.keys():
            currObjects["Student"] = request.query_params["studentID"]
        else:
            currObjects["Student"] = None

        if "worldID" in request.query_params.keys():
            currObjects["World"] = request.query_params["worldID"]
            noParams = False
        else:
            currObjects["World"] = None

        if "sectionID" in request.query_params.keys():
            currObjects["Section"] = request.query_params["sectionID"]
            noParams = False
        else:
            currObjects["Section"] = None
        
        if "levelID" in request.query_params.keys():
            currObjects["Level"] = request.query_params["levelID"]
            noParams = False
        else:
            currObjects["Level"] = None
            
        if "questionID" in request.query_params.keys():
            currObjects["Question"] = request.query_params["questionID"]
            noParams = False
        else:
            currObjects["Question"] = None
        
        if currObjects["Student"] != None:
            queryset = questionHistory.objects.filter(studentID__id = currObjects["Student"])
            noParams = False
        else:
            queryset = questionHistory.objects.all()

        if queryset.count() == 0:
            return render(request, 'dashboard.html', {
                'data': None
            })

        objList = dict()

        labels = ['Correct', 'Incorrect']
        data = [0, 0]
        backgroundColor = ['#2A9D8F', '#F4A261']

        objList["World"] = [str(x["worldID__name"]) for x in queryset.values("worldID__name").distinct()]
        
        if currObjects["World"] != None:
            queryset = queryset.filter(worldID__name = currObjects["World"])
            objList["Section"] = [str(x["sectionID__name"]) for x in queryset.values("sectionID__name").distinct()]
            if currObjects["Section"] != None:
                queryset = queryset.filter(sectionID__name = currObjects["Section"])
                objList["Level"] = [str(x["questionID__questionLevel"]) for x in queryset.values("questionID__questionLevel").distinct()]
                if currObjects["Level"] != None:
                    queryset = queryset.filter(questionID__questionLevel = currObjects["Level"])
                    objList["Question"] = [str(x["questionID__id"]) for x in queryset.values("questionID__id").distinct()]
                    if currObjects["Question"] != None:
                        queryset = queryset.filter(questionID__id=currObjects["Question"])

        scoreQuery = queryset.values('studentID').annotate(score=Count('studentID', filter=Q(isAnsweredCorrect=True)), ident=Case(
            When(studentID__name='', then='studentID__email'),
            default='studentID__name'
        ))
        studentScore = [(x['studentID'], x['ident'], x['score']) for x in scoreQuery]
        sortedScore = sorted(studentScore, key=lambda item: [2])
        
        orderedStudentIDList = [x[0] for x in sortedScore]
        orderedStudentList = [x[1] for x in sortedScore]
        orderedScoreList = [x[2] for x in sortedScore]

        scoreLevel = dict()
        scoreLevel["Max"] = max(orderedScoreList)
        scoreLevel["Min"] = min(orderedScoreList)
        scoreLevel["Mean"] = round(statistics.mean(orderedScoreList), 2)
        scoreLevel["Median"] = statistics.median(orderedScoreList)
        
        data[0] = queryset.filter(isAnsweredCorrect=True).count()
        data[1] = queryset.filter(isAnsweredCorrect=False).count()

        colorList = list()

        for i in range(len(orderedStudentList)):
            letters = '0123456789ABCDEF'
            color = '#'
            for j in range(6):
                color += letters[random.randint(0, len(letters) - 1)]
            colorList.append(color)

        studentScore = zip(colorList, orderedStudentIDList, orderedStudentList, orderedScoreList)
    
        return render(request, 'dashboard.html', {
            'labels': labels,
            'data': data,
            'backgroundColor': backgroundColor,
            'currObjects': currObjects,
            'objList': objList,
            'noParams': noParams,
            'studentScore': studentScore,
            'orderedStudentList': orderedStudentList,
            'orderedScoreList': orderedScoreList,
            'scoreLevel': scoreLevel,
            'colorList': colorList
        })

class signup(APIView):
    """
    View for Signup form

    Returns:
        HttpResponse: Response that contains all the variables used by sign_up.html template
    """
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        form = signupForm()

        return render(request, 'sign_up.html', {
            'form': form
        })
    
    def post(self, request):
        form = signupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            User.objects.create_superuser(email, password)
            return HttpResponseRedirect('/')
        
        return render(request, 'sign_up.html', {
            'form': form
        })
