from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication

from .serializer import TodoSerializer, TodoToggleCompleteSerializer
from todo.models import Todo
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
#from django.contrib.auth.models import AnonymousUser
# Create your views here.

class TodoList(generics.ListAPIView):
    serializer_class = TodoSerializer
    #permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        print(f"User: {user}, is authenticated: {user.is_authenticated}")
        #if isinstance(user, AnonymousUser):
            #return Todo.objects.none()  Return an empty queryset for anonymous user

        queryset = Todo.objects.filter(user = user).order_by('-created')
        print(f"Queryset count: {queryset.count()}")
        return queryset
class TodoListCreate(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication] #Extra


    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user = user).order_by('-created')

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class TodoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user = user)

class TodoToggleComplete(generics.UpdateAPIView):
    serializer_class = TodoToggleCompleteSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user = user)

    def perform_update(self, serializer):
        serializer.instance.completed = not(serializer.instance.completed)
        serializer.save()

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
            )
            user.save()

            token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=201)
        except IntegrityError:
            return JsonResponse(
                {'error':'username taken. choose another username'}, status=400
            )

from django.contrib.auth import authenticate
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(request, username = data['username'], password = data['password'])
        if user is None:
            return JsonResponse(
                {'error': 'unable to login. check username'}, status=400
            )
        else:
            try:
                token=Token.objects.get(user=user)
            except:
                token = Token.objects.create(user= user)
            print(f"Login successful for user: {user.username}, token: {token.key}")
            return JsonResponse({'token': str(token)}, status=201)
