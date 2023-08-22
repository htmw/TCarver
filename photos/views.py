from datetime import datetime
import os
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Category, Photo, Predict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
# Create your views here.
import cv2
from PIL import Image
import urllib.request
import numpy as np
import tensorflow as tf 
from django.template.response import TemplateResponse
from django.utils.datastructures import MultiValueDictKeyError

from django.core.files.storage import FileSystemStorage
from keras.applications.imagenet_utils import decode_predictions
from keras.preprocessing.image import img_to_array, load_img
from tensorflow.python.keras.backend import set_session
from keras.models import load_model
import boto3
import pandas as pd
import requests
import matplotlib.pyplot as plt
import pathlib
from pathlib import Path

def homePage(request):
    """Renders the home page."""
    return render(
        request,
        'photos/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    return render(
        request,
        'photos/contact.html',
        {
            'title':'Have questions about the App',
            'message':'Feel free to email or write to me at:.',
            'year':datetime.now().year,
        }
    )
def about(request):
    """Renders the about page."""
    return render(
        request,
        'photos/about.html',
        {
            'title':'This is how the magic works',
            'message':'IveSeenThat is a self-diagnosing, symptom-checking application that allows users to upload a picture of their illness area and receive a diagnosis based on an original Machine Learning algorithm.',
            'year':datetime.now().year,
        }
    )


def loginUser(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('gallery')

    return render(request, 'photos/login_register.html', {'page': page})


def logoutUser(request):
    logout(request)
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            if user is not None:
                login(request, user)
                return redirect('gallery')

    context = {'form': form, 'page': page}
    return render(request, 'photos/login_register.html', context)

def poxLibrary(request):
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path)
    context = {"images": img_list}
    return render (request, 'photos/chickenpox.html', context)

def pinkLibrary(request):
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path)
    context = {"images": img_list}
    return render (request, 'photos/pinkeye.html', context)


def photoLibrary(request):
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path)
    context = {"images": img_list}
    return render (request, 'photos/library.html', context)

@login_required(login_url='login')
def gallery(request):
    user = request.user
    category = request.GET.get('category')
    if category == None:
        photos = Photo.objects.filter(category__user=user)
    else:
        photos = Photo.objects.filter(
            category__name=category, category__user=user)

    categories = Category.objects.filter(user=user)
    context = {'categories': categories, 'photos': photos}
    return render(request, 'photos/gallery.html', context)


@login_required(login_url='login')
def viewPhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    return render(request, 'photos/photo.html', {'photo': photo})


@login_required(login_url='login')
def addPhoto(request):
    user = request.user

    categories = user.category_set.all()

    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('images')

        if data['category'] != 'none':
            category = Category.objects.get(id=data['category'])
        elif data['category_new'] != '':
            category, created = Category.objects.get_or_create(
                user=user,
                name=data['category_new'])
        else:
            category = None

        for image in images:
            photo = Photo.objects.create(
                category=category,
                description=data['description'],
                image=image,
            )

        return redirect('gallery')

    context = {'categories': categories}
    return render(request, 'photos/add.html', context)

@login_required(login_url='login')
def predictionPage(request, pk):
    photo = Photo.objects.get(id=pk)  
    try:
        # turn the image into a numpy array using the file name not the URL
        imag = np.array(Image.open(photo.image))
        # have to change it to the same specifications as your model
        resize = tf.image.resize(imag, (256,256))         
        # load model
        model = tf.keras.models.load_model(settings.IMAGE_MODEL)
        # extract the number (0 - 1) that will tell you what the image is
        result = model.predict(np.expand_dims(resize/255, 0 ))
         ## LABELS = pinkeye 1 / chickenpox 0
         # ----------------
        if result <= 0.01:
            prediction = "UNKNOWN!"
            confidence = "UNKNOWN"
        elif 0.01 <= result < 0.5:
            prediction = "Chicken Pox"
            # logic is: closer you are to the number zero the more confident the algorithm is
            # in assessing the picture to be chickenpox so input negative one to flip it and 
            # you will get a negative decimal then multiply by negative 100 to get positive percentage
            confidence = (round(float(result),3)-1)*-100
        elif 0.5 <= result <= 1:
            prediction = "Pink Eye"
            #logic is: the closer you are to the number 1 the more confident the algorithm is
            #in assessing the picture
            confidence = round(float(result),3)*100
        else:
            prediction = "Picture cannot be assessed"
            confidence = "zero"
         
        return TemplateResponse(
            request,
            'photos/prediction.html',
            {
                'message': 'Here is your photo',
                'photo': photo,
                'Result': result,
                'Confidence': confidence,
                "prediction": prediction,
            },
            )
    except MultiValueDictKeyError:

        return TemplateResponse(
            request,
            "photos/prediction.html",
            {"message": "No Image Selected"},
        )

    