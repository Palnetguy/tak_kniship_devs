from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, Group
from django.contrib.auth.models import AbstractUser
from rest_framework_api_key.models import AbstractAPIKey


class TechStack(models.Model):
    language = models.TextField()

    def __str__(self):
        return self.language

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('Mobile App', 'Mobile App'),
        ('Web', 'Web'),
        ('Desktop', 'Desktop'),
    ]
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    project_background_image = models.ImageField(upload_to='project_images')
    tech_stack =  models.ManyToManyField(TechStack,null=True, blank=True)
    description = models.TextField()
    project_goals = models.TextField()
    target_audience = models.TextField()
    project_category = models.CharField(max_length=100)
    date_published = models.DateField()
    duration_of_development = models.IntegerField()

    def __str__(self):
        return self.title
     
class TeamMember(models.Model):
    profile_picture = models.ImageField(upload_to='team_images')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    instagram = models.CharField(max_length=100)
    linkedin = models.CharField(max_length=100)
    twitter = models.CharField(max_length=100)
    skype = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    user_photo = models.ImageField(upload_to='testimonial_images')
    name = models.CharField(max_length=100)
    comment = models.TextField()
    job_title = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery_images')


class FAQ(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
    

class ContactUsMessage(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    phone_number = models.CharField(max_length=20)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    
class ContactInfo(models.Model):
    company_name = models.CharField(max_length=300)
    location = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    instgram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    skype  = models.URLField(blank=True)
    linkedIn = models.URLField(blank=True)

    def __str__(self):
        return self.company_name

class WorkExperience(models.Model):
    no_of_clients = models.IntegerField()
    no_of_complete_projects = models.IntegerField()
    years_of_experience = models.IntegerField()
    no_of_workers = models.IntegerField(default=2)
    desktop_dev = models.IntegerField(default=40)
    mobile_dev = models.IntegerField(default=70)
    web_dev = models.IntegerField(default=55)
    ui_dev = models.IntegerField(default=20)

class MobileApplication(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    icon = models.ImageField(upload_to='App_icons/')
    apk = models.FileField(upload_to='Apks/', null=True)
    apk_url = models.URLField(blank=True)
    download_id =  models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    date_released = models.DateField(auto_now=True, blank=True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class DesktopApplication(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    icon = models.ImageField(upload_to='App_icons/')
    apk = models.FileField(upload_to='Apks/', null=True)
    apk_url = models.URLField(blank=True)
    download_id =  models.CharField(max_length=100,blank=True)
    description = models.TextField(blank=True)
    date_released = models.DateField(auto_now=True, blank=True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class WebApplication(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='WebApp_Icons/')
    url = models.URLField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# class User(AbstractUser, AbstractAPIKey):
#     pass