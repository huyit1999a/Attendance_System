from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    AdminHOD,
    Employee,
    Attendance,
)

# Register your models here.


class UserModel(UserAdmin):
    pass


admin.site.register(CustomUser, UserModel)
admin.site.register(AdminHOD)
admin.site.register(Employee)
admin.site.register(Attendance)
