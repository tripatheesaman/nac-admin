from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserLoginForm, UserPasswordChangeForm
from .models import User
from django.conf import settings


class UserLoginView(LoginView):
    """Custom login view"""
    template_name = 'processor/auth/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('processor:home')
    
    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)



@login_required
def user_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('processor:login')


@login_required(login_url='/app/login/')
def change_password(request):
    """Password change view"""
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed successfully.")
            return redirect('processor:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserPasswordChangeForm(request.user)
    
    return render(request, 'processor/auth/change_password.html', {'form': form})


@login_required(login_url='/app/login/')
def profile(request):
    """User profile view"""
    return render(request, 'processor/auth/profile.html') 