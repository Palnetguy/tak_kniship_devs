from django.contrib import admin

from tak_devs_app.models import FAQ, Agreement, ContactInfo, ContactUsMessage, DesktopApplication, Gallery, MobileApplication, Project, TeamMember, TechStack, Testimonial, WebApplication, WorkExperience

admin.site.register(Project)
admin.site.register(Agreement)
admin.site.register(TeamMember)
admin.site.register(Testimonial)
admin.site.register(FAQ)
admin.site.register(ContactUsMessage)
admin.site.register(WorkExperience)
admin.site.register(MobileApplication)
admin.site.register(DesktopApplication)
admin.site.register(WebApplication)
admin.site.register(Gallery)
admin.site.register(TechStack)
admin.site.register(ContactInfo)