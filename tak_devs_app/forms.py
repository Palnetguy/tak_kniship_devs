from django import forms
from .models import Testimonial, ProjectClient

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'job_title', 'comment', 'user_photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Job Title'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Share your experience working with TAK Kinship...', 'rows': 5}),
            'user_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ProjectClientFeedbackForm(forms.ModelForm):
    class Meta:
        model = ProjectClient
        fields = ['name', 'location', 'rating', 'message', 'profile_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Location'}),
            'rating': forms.RadioSelect(attrs={'class': 'visually-hidden'}, choices=[(i, i) for i in range(1, 6)]),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Please share your feedback about the project...', 'rows': 5}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }