from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),

    path('gallery/', views.gallery, name='gallery'),
    path('photo/<str:pk>/', views.viewPhoto, name='photo'),
    path('add/', views.addPhoto, name='add'),
    
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('', views.homePage, name='home'),
    path('library/', views.photoLibrary, name='library'),
    path('chickenpox/', views.poxLibrary, name='chickenpox'),
    path('pinkeye/', views.pinkLibrary, name='pinkeye'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)