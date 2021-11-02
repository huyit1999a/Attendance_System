from django.urls import path, include
from . import views
from . import HodViews, EmployeeViews


urlpatterns = [
    path("", views.loginPage, name="login"),
    # path('accounts/', include('django.contrib.auth.urls')),
    path("doLogin/", views.doLogin, name="doLogin"),
    path("get_user_details/", views.get_user_details, name="get_user_details"),
    path("logout_user/", views.logout_user, name="logout_user"),
    path("admin_home/", HodViews.admin_home, name="admin_home"),
    path("manage_department/", HodViews.manage_department,
         name="manage_department"),
    path("add_department/", HodViews.add_department, name="add_department"),
    path(
        "add_department_save/", HodViews.add_department_save, name="add_department_save"
    ),
    path(
        "edit_department/<department_id>/",
        HodViews.edit_department,
        name="edit_department",
    ),
    path(
        "edit_department_save/",
        HodViews.edit_department_save,
        name="edit_department_save",
    ),
    path(
        "delete_department/<department_id>/",
        HodViews.delete_department,
        name="delete_department",
    ),
    path("add_employee/", HodViews.add_employee, name="add_employee"),
    path("add_employee_save/", HodViews.add_employee_save,
         name="add_employee_save"),
    path("edit_employee/<employee_id>",
         HodViews.edit_employee, name="edit_employee"),
    path("edit_employee_save/", HodViews.edit_employee_save,
         name="edit_employee_save"),
    path("manage_employee/", HodViews.manage_employee, name="manage_employee"),
    path(
        "delete_employee/<employee_id>/", HodViews.delete_employee, name="delete_employee"
    ),
    path("check_email_exist/", HodViews.check_email_exist,
         name="check_email_exist"),
    path(
        "check_username_exist/",
        HodViews.check_username_exist,
        name="check_username_exist",
    ),
    path("admin_profile/", HodViews.admin_profile, name="admin_profile"),
    path(
        "admin_profile_update/",
        HodViews.admin_profile_update,
        name="admin_profile_update",
    ),
    # URSL for employee
    path("employee_home/", EmployeeViews.employee_home, name="employee_home"),
    path(
        "employee_view_attendance/",
        EmployeeViews.employee_view_attendance,
        name="employee_view_attendance",
    ),
    path("employee_profile/", EmployeeViews.employee_profile,
         name="employee_profile"),
    path(
        "employee_profile_update/",
        EmployeeViews.employee_profile_update,
        name="employee_profile_update",
    ),
    path("take_attendance/", HodViews.take_attendance, name="take_attendance"),
    path("detect_with_webcam/", HodViews.detect_with_webcam,
         name="detect_with_webcam"),
    path("manage_attendance/", HodViews.manage_attendance,
         name="manage_attendance"),
    path("admin_view_attendance/", HodViews.admin_view_attendance,
         name="admin_view_attendance"),
    path("export_excel/", HodViews.export_excel, name="export_excel"),
]
