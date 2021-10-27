from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from datetime import datetime  # To Parse input DateTime into Python Date Time Object
from django.core.paginator import Paginator

from employee_management_app.models import (
    CustomUser,
    Employee,
    Attendance,
)


def employee_home(request):
    employee = Employee.objects.get(admin=request.user.id)
    total_attendance = Attendance.objects.filter(
        employee_id=employee.id).count()
    context = {
        "employee": employee,
        "total_attendance": total_attendance
    }
    return render(request, "employee_template/employee_home_template.html", context)


def employee_view_attendance(request):
    employee = Employee.objects.get(admin=request.user.id)
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if end_date < start_date:
            messages.error(request, "Ngày kết thúc phải lớn hơn ngày bắt đầu")
            return redirect('manage_attendance')
        # Parsing the date data into Python object
        else:
            start_date_parse = datetime.strptime(
                start_date, '%Y-%m-%d').date()
            end_date_parse = datetime.strptime(
                end_date, '%Y-%m-%d').date()

            attendance_report = Attendance.objects.filter(
                attendance_date__range=(start_date_parse, end_date_parse), employee_id=employee.id)

            context = {
                "data": attendance_report,
                "employee": employee,
            }

            return render(request, "employee_template/employee_view_attendance.html", context)
    else:
        data = Attendance.objects.filter(employee_id=employee.id)

        paginator = Paginator(data, per_page=8)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            "data": page_obj.object_list,
            "paginator": paginator,
            "page_number": int(page_number),
            "employee": employee,
        }
        return render(request, "employee_template/employee_view_attendance.html", context)


def employee_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    employee = Employee.objects.get(admin=user)

    context = {"user": user, "employee": employee}
    return render(request, "employee_template/employee_profile.html", context)


def employee_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect("employee_profile")
    else:

        password = request.POST.get("password")
        address = request.POST.get("address")

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            employee = Employee.objects.get(admin=customuser.id)
            employee.address = address

            employee.save()

            messages.success(request, "Cập nhật hồ sơ thành công")
            return redirect("employee_profile")
        except:
            messages.error(request, "Cập nhật hồ sơ thất bại")
            return redirect("employee_profile")
