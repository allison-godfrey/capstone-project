from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Person)
admin.site.register(Course)
admin.site.register(Response)
admin.site.register(Assignment)
admin.site.register(Question)
admin.site.register(Enrollment)