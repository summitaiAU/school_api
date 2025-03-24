from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolViewSet, SchoolClassViewSet, StudentViewSet, 
    import_excel_data, import_page, add_school, add_class, add_student
)

router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'classes', SchoolClassViewSet)
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('import-excel/', import_excel_data, name='import-excel'),
    path('import/', import_page, name='import-page'),
    
    # New simple endpoints for automation tools
    path('add-school/', add_school, name='add-school'),
    path('add-class/', add_class, name='add-class'),
    path('add-student/', add_student, name='add-student'),
]