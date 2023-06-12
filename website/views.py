import requests
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from .forms import NewUserForm


class HomePageView(View):
    template_name = 'website/home.html'

    def get(self, request):
        pokemon_list_url = 'https://pokeapi.co/api/v2/pokemon/?limit=20'
        pokemon_list = requests.get(pokemon_list_url).json()
        next_pokemons = pokemon_list['next']
        print(next_pokemons)
        previous_pokemons = pokemon_list['previous']
        pokemon_list = pokemon_list['results']
        context = {"pokemon_list": pokemon_list,
                   "next_pokemons": next_pokemons,
                   "previous_pokemons": previous_pokemons,
                   }
        return render(request, self.template_name, context)


class RegisterView(View):
    template_name = 'website/register.html'
    form_class = NewUserForm

    def get(self, request):
        form = self.form_class
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("home")
        else:
            messages.error(request, "Unsuccessful registration - invalid information.")
            context = {"form": form}
            return render(request, self.template_name, context)

class LoginView(View):
    template_name = 'website/login.html'
    form_class = AuthenticationForm

    def get(self, request):
        form = self.form_class
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is None:
                messages.error(request, "Invalid username or password")
            else:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            context = {"form": form}
            return render(request, self.template_name, context)

class LogoutView(View):

    def get(self, request):
        logout(request)
        messages.info(request, "You have successfully logged out.")
        return redirect("home")
