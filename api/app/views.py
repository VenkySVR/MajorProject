# from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
# from yaml import serialize
from .serializers import ProblemSerializer, TestCasesSerializer, SubmissionsSerializer, UserSerializer, CodeSerializer
from .models import Problem, TestCases, Submissions, CustomUser
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from .run_code import run_code
# from .code import Run,Submit
# Create your views here.
from django.shortcuts import render,redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import requests

from django.views.decorators.csrf import csrf_protect


@api_view(['GET'])
def Problem_post(request):
    if request.method == 'GET':
        serializer = ProblemSerializer(Problem.objects.all(), many=True)
        return Response(serializer.data)

@api_view(['GET'])
def Problem_detail(request, id):
    try:
        problem = Problem.objects.get(id=id)
    except Problem.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'GET':
        serializer = ProblemSerializer(problem)
        return Response(serializer.data)

@api_view(['GET'])
def Leadership(request):
    if request.method == 'GET':
        serializer = UserSerializer(CustomUser.objects.all(), many=True)
        return Response(serializer.data)

@api_view(['GET'])
def ListOfSubmissionsOfProblem(request, id):
    try:
        problem = Problem.objects.get(id=id)
    except Problem.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'GET':
        serializer = SubmissionsSerializer(Submissions.objects.filter(problem=problem), many=True)
        return Response(serializer.data)

@api_view(['GET'])
def ListOfSubmissionsOfUser(request,id):
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'GET':
        serializer = SubmissionsSerializer(Submissions.objects.filter(user=user), many=True)
        return Response(serializer.data)

# @csrf_exempt
# @api_view(['POST'])
# def Code_post(request):
#     if request.method == 'POST':
#         serializer = CodeSerializer(data=request.data)
#         if serializer.is_valid():
#             # print(serializer.data)
#             # serializer.save()
#             if serializer.data['user_id'] == None and serializer.data['problem_id'] == None:
#                 output = Run(serializer.data['code'],serializer.data['language'],serializer.data['input'])
#             else:
#                 output = Submit(serializer.data['code'],serializer.data['language'],serializer.data['problem_id'],serializer.data['user_id'])
#                 # output['result'] = output['result'].replace('\n','<br>')
#                 print(output)
#             return Response(output, status=201)
#         return Response(serializer.errors, status=400)


