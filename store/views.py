from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import UpdateView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import *
from .forms import *


data = {
    'products': Product.objects.all(),
}

def index(request):
    data['products'] = Product.objects.all()
    return render(request, 'store/index.html', context=data)


def about(request):
    return render(request, 'store/about.html', context=data)


def detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    data['product'] = product
    return render(request, 'store/product.html', context=data)


def category(request, pk):
    category = get_object_or_404(Category, id=pk)
    title_category = get_object_or_404(Category, id=pk)
    products = category.products.all()
    data['products'] = products
    data['title_category'] = title_category
    return render(request, 'store/category.html', context=data)

def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = authenticate(username=cleaned_data["username"], password=cleaned_data["password"])
            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, ("You are now logged in successfully!"))
                return HttpResponseRedirect(reverse('index'))
    data['form'] = form
    return render(request, 'store/login.html', context=data)


def user_logout(request):
    logout(request)
    messages.success(request, ("You are now logged out successfully!"))
    return HttpResponseRedirect(reverse('login'))


def user_register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return HttpResponseRedirect(reverse('login'))
    data['form'] = form
    return render(request, 'store/register.html', context=data)


class ProfileUserView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
        model = get_user_model()
        form_class = ProfileForm
        template_name = 'store/profile_form.html'
        success_message = "%(username)s updated profile successfully"
        data['form'] = ProfileForm()

        def get_success_url(self):
            return reverse_lazy('profile')

        def get_object(self):
            return self.request.user


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'store/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

