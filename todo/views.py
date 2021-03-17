from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request,'todo/home.html')

#User========================================
def signUpUser(request):
    if request.method == 'GET':
        return render(request,'todo/signUpUser.html',{'form':UserCreationForm()})
    else:
        #Create a new User
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('currentTodos')

            except IntegrityError:
                return render(request,'todo/signUpUser.html',{'form':UserCreationForm(),'error':'That username has already been taken. Please choose a new Username.'})
            except ValueError:
                return render(request,'todo/signUpUser.html',{'form':UserCreationForm(),'error':'An error occur'})
        else:
            #password didnt match
            return render(request,'todo/signUpUser.html',{'form':UserCreationForm(),'error':'Passwords did not match'})

def loginUser(request):
    if request.method == 'GET':
        return render(request,'todo/loginUser.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,'todo/loginUser.html',{'form':AuthenticationForm(),'error':'Username and password did not match'})
        else:
            login(request,user)
            return redirect('currentTodos')

@login_required
def logoutUser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

#Todos==============================================
@login_required
def currentTodos(request):
    todos = Todo.objects.filter(user=request.user,dateFinished__isnull=True)
    return render(request,'todo/currentTodos.html',{'todos':todos})

@login_required
def createTodo(request):
    if request.method == 'GET':
        return render(request,'todo/createTodo.html',{'form':TodoForm()})
    else:
        try:
            #Create a new Todo
            form = TodoForm(request.POST)
            newTodo = form.save(commit=False)
            newTodo.user = request.user
            newTodo.save()
            return redirect('currentTodos')
        except ValueError:
                return render(request,'todo/createTodo.html',{'form':TodoForm(),'error':'An error occur.'})

@login_required
def viewTodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request,'todo/viewTodo.html',{'todo':todo,'form':form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currentTodos')
        except ValueError:
                return render(request,'todo/viewTodo.html',{'todo':todo,'form':form,'error':'An error occur.'})

@login_required
def completeTodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.dateFinished = timezone.now()
        todo.save()
        return redirect('currentTodos')

@login_required
def deleteTodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currentTodos')

@login_required
def completeTodos(request):
    todos = Todo.objects.filter(user=request.user,dateFinished__isnull=False).order_by('-dateFinished')
    return render(request,'todo/completeTodos.html',{'todos':todos})
