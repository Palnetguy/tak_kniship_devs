from django.db import models
from cloudinary.models import CloudinaryField

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('Mobile App', 'Mobile App'),
        ('Web', 'Web'),
        ('Desktop', 'Desktop'),
    ]
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    project_background_image = CloudinaryField('TAK/TAK_KNISHIP_DEVS/project_images')
    tech_stack = models.TextField()
    description = models.TextField()
    project_goals = models.TextField()
    target_audience = models.TextField()
    project_category = models.CharField(max_length=100)
    date_published = models.DateField()
    duration_of_development = models.IntegerField()
     
class TeamMember(models.Model):
    profile_picture = CloudinaryField('TAK/TAK_KNISHIP_DEVS/team_images')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    instagram = models.CharField(max_length=100)
    linkedin = models.CharField(max_length=100)
    twitter = models.CharField(max_length=100)
    skype = models.CharField(max_length=100)

class Testimonial(models.Model):
    user_photo = CloudinaryField('TAK/TAK_KNISHIP_DEVS/testimonial_images')
    name = models.CharField(max_length=100)
    comment = models.TextField()
    job_title = models.CharField(max_length=100)

class Gallery(models.Model):
    photo = CloudinaryField('TAK/TAK_KNISHIP_DEVS/gallery_images')

class FAQ(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

class ContactUsMessage(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    phone_number = models.CharField(max_length=20)
    date_sent = models.DateTimeField(auto_now_add=True)

class WorkExperience(models.Model):
    no_of_clients = models.IntegerField()
    no_of_complete_projects = models.IntegerField()
    years_of_experience = models.IntegerField()

class MobileApplication(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    icon = models.ImageField(upload_to='app_icons/')
    apk = models.FileField(upload_to='TAK_KNISHIP_DEVS/apks/')
    url = models.URLField(blank=True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

class DesktopApplication(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    icon = models.ImageField(upload_to='app_icons/')
    apk = models.FileField(upload_to='TAK_KNISHIP_DEVS/apks/')
    url = models.URLField(blank=True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)

class WebApplication(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='app_icons/')
    url = models.URLField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
