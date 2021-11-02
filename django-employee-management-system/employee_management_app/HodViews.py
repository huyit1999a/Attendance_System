from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import cv2
import os
import xlwt
from datetime import datetime
from django.core.paginator import Paginator

from employee_management_app.models import (
    CustomUser,
    Departments,
    Employee,
    Attendance,
)
from .forms import AddEmployeeForm, EditEmployeeForm


def admin_home(request):
    all_employee_count = Employee.objects.all().count()
    all_department_count = Departments.objects.all().count()

    context = {
        "all_employee_count": all_employee_count,
        "all_department_count": all_department_count
    }
    return render(request, "hod_template/home_content.html", context)


def take_attendance(request):
    return render(request, "hod_template/take_attendance_template.html")


def add_department(request):
    return render(request, "hod_template/add_department_template.html")


def add_department_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect("add_department")
    else:
        department = request.POST.get("department")
        try:
            department_model = Departments(department_name=department)
            department_model.save()
            messages.success(request, "Thêm phòng ban thành công!")
            return redirect("manage_department")
        except:
            messages.error(request, "Thêm phòng ban thất bại!")
            return redirect("add_department")


def manage_department(request):
    departments = Departments.objects.all()
    context = {"departments": departments}
    return render(request, "hod_template/manage_department_template.html", context)


def edit_department(request, department_id):
    department = Departments.objects.get(id=department_id)
    context = {"department": department, "id": department_id}
    return render(request, "hod_template/edit_department_template.html", context)


def edit_department_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        department_id = request.POST.get("department_id")
        department_name = request.POST.get("department_name")

        try:
            department = Departments.objects.get(id=department_id)
            department.department_name = department_name
            department.save()

            messages.success(request, "Cập nhật tên phòng ban thành công")
            return redirect("manage_department")

        except:
            messages.error(request, "Cập nhật thất bại")
            return redirect("/edit_department/" + department_id)


def delete_department(request, department_id):
    department = Departments.objects.get(id=department_id)
    try:
        department.delete()
        messages.success(request, "Xóa phòng ban thành công.")
        return redirect("manage_department")
    except:
        messages.error(request, "Xóa thất bại.")
        return redirect("manage_department")


def add_employee(request):
    form = AddEmployeeForm()
    context = {"form": form}
    return render(request, "hod_template/add_employee_template.html", context)


def add_employee_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect("add_employee")
    else:
        form = AddEmployeeForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data["name"]
            last_name = form.cleaned_data["name"]
            username = form.cleaned_data["email"]
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            address = form.cleaned_data["address"]
            department_id = form.cleaned_data["department_id"]
            gender = form.cleaned_data["gender"]

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES["profile_pic"]
                # fs = FileSystemStorage()
                # filename = fs.save(profile_pic.name, profile_pic)
                # profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=2,
                )
                user.employee.address = address
                department_obj = Departments.objects.get(id=department_id)
                user.employee.department_id = department_obj

                user.employee.name = name
                user.employee.gender = gender
                user.employee.profile_pic = profile_pic

                user.save()
                messages.success(request, "Thêm nhân viên thành công!")
                return redirect("manage_employee")
            except:
                messages.error(request, "Thêm nhân viên thất bại!")
                print(form.errors)
                return redirect("add_employee")
        else:
            return redirect("add_employee")


def manage_employee(request):
    employees = Employee.objects.all()
    context = {"employees": employees}
    return render(request, "hod_template/manage_employee_template.html", context)


def edit_employee(request, employee_id):
    # Adding employee ID into Session Variable
    request.session["employee_id"] = employee_id
    employee = Employee.objects.get(admin=employee_id)
    form = EditEmployeeForm()

    # Filling the form with Data from Database
    form.fields["email"].initial = employee.admin.email
    # form.fields["password"].initial = employee.admin.password
    form.fields["name"].initial = employee.name
    form.fields["address"].initial = employee.address
    form.fields["department_id"].initial = employee.department_id.id
    form.fields["gender"].initial = employee.gender

    context = {"id": employee_id, "form": form}
    return render(request, "hod_template/edit_employee_template.html", context)


def edit_employee_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        employee_id = request.session.get("employee_id")
        if employee_id == None:
            return redirect("/manage_employee")

        form = EditEmployeeForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["name"]
            last_name = form.cleaned_data["name"]
            name = form.cleaned_data["name"]
            address = form.cleaned_data["address"]
            department_id = form.cleaned_data["department_id"]
            gender = form.cleaned_data["gender"]

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES["profile_pic"]
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=employee_id)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                # Then Update employees Table
                employee_model = Employee.objects.get(admin=employee_id)
                employee_model.address = address

                department_obj = Departments.objects.get(id=department_id)
                employee_model.department_id = department_obj
                employee_model.name = name
                employee_model.gender = gender
                if profile_pic_url != None:
                    employee_model.profile_pic = profile_pic_url
                employee_model.save()
                # Delete employee_id SESSION after the data is updated
                del request.session["employee_id"]

                messages.success(request, "Cập nhật nhân viên thành công")
                return redirect("/manage_employee/")
            except:
                return redirect("/edit_employee/" + employee_id)
        else:
            messages.error(request, "Cập nhật nhân viên thất bại")
            print(form.errors)
            return redirect("/edit_employee/" + employee_id)


def delete_employee(request, employee_id):
    employee = Employee.objects.get(admin=employee_id)
    user = CustomUser.objects.get(id=employee_id)

    try:
        if len(employee.profile_pic) > 0:
            os.remove(employee.profile_pic.path)

        employee.delete()
        user.delete()
        messages.success(request, "Xóa nhân viên thành công")
        return redirect("manage_employee")
    except:
        messages.error(request, "Xóa nhân viên thất bại")
        print(employee.profile_pic.path)
        return redirect("manage_employee")


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context = {"user": user}
    return render(request, "hod_template/admin_profile.html", context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect("admin_profile")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("admin_profile")
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect("admin_profile")


def employee_profile(request):
    pass


def detect_with_webcam(request):
    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    images = []
    encodings = []
    names = []
    files = []
    employeeIds = []
    departmentIds = []

    employees = Employee.objects.all()

    for employee in employees:
        images.append(employee.name + "_image")
        encodings.append(employee.name + "_face_encoding")
        files.append(employee.profile_pic)
        names.append(employee.name)  # + "\nID: " + str(employee.id)
        departmentIds.append(employee.department_id)
        employeeIds.append(employee.id)

    for i in range(0, len(images)):
        images[i] = face_recognition.load_image_file(files[i])
        encodings[i] = face_recognition.face_encodings(images[i])[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = encodings
    known_face_names = names
    employee_ids = employeeIds
    department_ids = departmentIds

    while True:
        # Grab a single img of video
        ret, img = video_capture.read()

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Find all the faces and face enqcodings in the img of video
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        # Loop through each face in this img of video
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(
                known_face_encodings, encodeFace)

            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(
                known_face_encodings, encodeFace
            )
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = (
                    known_face_names[best_match_index]
                )
                department = department_ids[best_match_index]
                employee_id = employee_ids[best_match_index]

                employee_obj = Employee.objects.get(id=employee_id)

                today = datetime.now()
                day = today.date()
                time = today.strftime("%H:%M:%S")
                exist = False

                try:
                    attendance_exist = Attendance.objects.get(
                        employee_id=employee_id, attendance_date=day)
                except:
                    attendance_exist = None

                if attendance_exist:
                    exist = True
                else:
                    employee_attendance = Attendance.objects.create(
                        employee_id=employee_obj,
                        name=employee_obj.name,
                        attendance_date=day,
                        attendance_time=time,
                    )

                    employee_attendance.save()

            # Draw a box around the face
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw a label with a name below the face
            cv2.rectangle(img, (x1, y2), (x2, y2),
                          (0, 255, 0), cv2.FILLED)
            if exist:
                cv2.putText(img, "Name: " + name, (x1 - 20, y2 - 230),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, "Diem danh thanh cong", (x1 - 20, y2 - 190),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            else:
                cv2.putText(img, "ID: " + str(employee_id), (x1 - 20, y2 - 230),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, "Name: " + name, (x1 - 20, y2 - 190),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        # Display the resulting image
        cv2.imshow("Video", img)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    return redirect("/manage_attendance")


def manage_attendance(request):
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
                attendance_date__range=(start_date_parse, end_date_parse))

            context = {
                "data": attendance_report,
            }

            return render(request, "hod_template/manage_attendance_template.html", context)
    else:
        data = Attendance.objects.all()
        paginator = Paginator(data, per_page=8)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            "data": page_obj.object_list,
            "paginator": paginator,
            "page_number": int(page_number),
        }
        return render(request, "hod_template/manage_attendance_template.html", context)


def admin_view_attendance(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_view_attendance')
    else:
        # Getting all the Input Data
        today = datetime.now()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Parsing the date data into Python object
        start_date_parse = datetime.strptime(
            start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.strptime(
            end_date, '%Y-%m-%d').date()

        attendance_report = Attendance.objects.filter(
            attendance_date__range=(start_date_parse, end_date_parse))

        context = {
            "attendance_report": attendance_report
        }

        return render(request, 'hod_template/manage_attendance_template.html', context)


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Diemdanh' + \
        str(datetime.now().date())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Diemdanh')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    colums = ['ID', 'HO TEN', 'NGAY', 'THOI GIAN']

    for col_num in range(len(colums)):
        ws.write(row_num, col_num, colums[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Attendance.objects.all().values_list(
        'employee_id', 'name', 'attendance_date', 'attendance_time')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)

    return response
