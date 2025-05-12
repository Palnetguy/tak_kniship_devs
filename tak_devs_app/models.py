from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, Group
from django.contrib.auth.models import AbstractUser
from rest_framework_api_key.models import AbstractAPIKey
from django.db.models.signals import post_save
from django.dispatch import receiver


class TechStack(models.Model):
    language = models.TextField()

    def __str__(self):
        return self.language

class Project(models.Model):
    PROJECT_CATEGORY_CHOICES = [
        ('Mobile App', 'Mobile App'),
        ('Web Application', 'Web Application'),
        ('Desktop Application', 'Desktop Application'),
    ]
    title = models.CharField(max_length=255, db_index=True)
    project_category = models.CharField(
        max_length=50, 
        choices=PROJECT_CATEGORY_CHOICES, 
        db_index=True
    )
    tech_stack = models.ManyToManyField(TechStack, blank=True)
    quote = models.CharField(max_length=255, blank=True)
    about_project = models.TextField()
    challenges_faced = models.TextField(blank=True)
    date_published = models.DateField(db_index=True)
    duration_of_development = models.IntegerField()

    @property
    def background_image(self):
        return self.images.filter(image_type='background').first()

    @property
    def about_images(self):
        return self.images.filter(image_type='about')

    @property
    def challenge_images(self):
        return self.images.filter(image_type='challenge')

    @property
    def gallery_images(self):
        return self.images.filter(image_type='gallery')

    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [
            models.Index(fields=['project_category']),
            models.Index(fields=['date_published']),
        ]

class ProjectImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('background', 'Background Image'),
        ('about', 'About Image'),
        ('challenge', 'Challenge Image')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')  # Make sure related_name is 'images'
    image = models.ImageField(upload_to='project_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['image_type']),
        ]

    def __str__(self):
        return f"{self.project.title} - {self.get_image_type_display()}"

class Agreement(models.Model):
    AGREEMENT_TYPE_CHOICES = [
        ('Terms', 'Terms'),
        ('Policy', 'Policy'),
       
    ]
    title = models.CharField(max_length=255)
    agreement_type = models.CharField(max_length=20, choices=AGREEMENT_TYPE_CHOICES)
    description = models.TextField()
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    date_published = models.DateField()

    def __str__(self):
        return f"{self.project.title} - {self.agreement_type}"





class TeamMember(models.Model):
    profile_picture = models.ImageField(upload_to='team_images')
    name = models.CharField(max_length=100, db_index=True)
    role = models.CharField(max_length=50, db_index=True)
    biography = models.TextField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    linkedin = models.CharField(max_length=100)
    twitter = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)  # New field for ordering

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']  # Order by the 'order' field, then by name
        indexes = [
            models.Index(fields=['order']),
        ]

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
    
    class Meta:
        indexes = [
            models.Index(fields=['date_sent']),
        ]

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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='mobile_applications')

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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='desktop_applications')

    def __str__(self):
        return self.name

class WebApplication(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='WebApp_Icons/')
    url = models.URLField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='web_applications')

    def __str__(self):
        return self.name


class ProjectFeature(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='features')

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class ProjectClient(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating
    message = models.TextField()
    profile_image = models.ImageField(upload_to='client_images/', null=True, blank=True)  # New optional field
    project = models.OneToOneField('Project', on_delete=models.CASCADE, related_name='client')

    def __str__(self):
        return f"{self.project.title} - {self.name}"

