from django.urls import path
from . import views
from . import auth_views

app_name = 'processor'

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
    path('profile/', auth_views.profile, name='profile'),
    path('change-password/', auth_views.change_password, name='change_password'),
    
    # Main Application URLs
    path('', views.HomeView.as_view(), name='home'),
    path('files/', views.FileListView.as_view(), name='file_list'),
    path('files/<int:file_id>/', views.FileDetailView.as_view(), name='file_detail'),
    path('files/<int:file_id>/download/', views.DownloadView.as_view(), name='download'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('files/<int:file_id>/preview/', views.preview_data, name='preview_data'),
    path('process/<int:file_id>/', views.ProcessFileView.as_view(), name='process_file'),
    
    
    # Progress polling endpoint
    path('progress/<int:progress_id>/', views.get_progress, name='get_progress'),
    # Staff Management URLs
    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/add/', views.StaffCreateView.as_view(), name='staff_add'),
    path('staff/<int:staff_id>/edit/', views.StaffUpdateView.as_view(), name='staff_edit'),
    path('staff/<int:staff_id>/delete/', views.delete_staff, name='staff_delete'),
    
    # Report Generation URLs
    path('files/<int:file_id>/segregation-report/', views.generate_segregation_report, name='generate_segregation_report'),
    path('files/<int:file_id>/leave-details/', views.get_detailed_leave_details, name='get_detailed_leave_details'),
    path('files/<int:file_id>/detailed-attendance-report/', views.generate_detailed_attendance_report, name='generate_detailed_attendance_report'),
    path('files/<int:file_id>/detailed-attendance/', views.generate_detailed_attendance_report, name='generate_detailed_attendance_report_short'),
    path('files/<int:file_id>/monthly-wages-report/', views.generate_monthly_wages_report, name='generate_monthly_wages_report'),
] 