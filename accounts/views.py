from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .form import SignupForm

# Create your views here.


def signup(requests):
    form = SignupForm()
    if requests.method == 'POST':
        form = SignupForm(requests.POST)
        # print(form)
        if form.is_valid():
            user = form.save()
            auth_login(requests,user)
            return redirect('index')
        # email = requests.POST['email']
        # password = requests.POST['password']
    return render(requests, 'signup.html', {'form': form})
