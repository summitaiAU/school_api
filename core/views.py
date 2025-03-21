from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import School, SchoolClass, Student
from .serializers import SchoolSerializer, SchoolClassSerializer, StudentSerializer
import pandas as pd

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

@api_view(['POST'])
def import_excel_data(request):
    """Import all data from an Excel file"""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
    file = request.FILES['file']
    
    # Print debug info
    print(f"Processing file: {file.name}")
    print(f"File size: {file.size} bytes")
    
    if not file.name.endswith('.xlsx'):
        return Response({'error': 'File format not supported. Please upload an Excel (.xlsx) file.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    results = {
        'schools_created': 0,
        'classes_created': 0,
        'students_created': 0,
        'errors': []
    }
    
    try:
        # Read Excel file
        excel_data = pd.ExcelFile(file)
        
        # Debug info
        print(f"Sheets in file: {excel_data.sheet_names}")
        
        # Process Schools sheet if it exists
        if 'Schools' in excel_data.sheet_names:
            schools_df = pd.read_excel(excel_data, 'Schools')
            print(f"Schools sheet columns: {schools_df.columns.tolist()}")
            for _, row in schools_df.iterrows():
                if pd.notna(row.get('name')) and row.get('name') != '':
                    try:
                        school, created = School.objects.get_or_create(
                            name=row.get('name'),
                            defaults={
                                'address': row.get('address', ''),
                                'phone': row.get('phone', ''),
                                'email': row.get('email', '')
                            }
                        )
                        if created:
                            results['schools_created'] += 1
                    except Exception as e:
                        results['errors'].append(f"Error creating school {row.get('name', '')}: {str(e)}")
        
        # Process Classes sheet if it exists
        if 'Classes' in excel_data.sheet_names:
            classes_df = pd.read_excel(excel_data, 'Classes')
            for _, row in classes_df.iterrows():
                if pd.notna(row.get('name')) and row.get('name') != '' and pd.notna(row.get('school_name')) and row.get('school_name') != '':
                    try:
                        # Get or create the associated school
                        school_name = row.get('school_name', '')
                        try:
                            school = School.objects.get(name=school_name)
                        except School.DoesNotExist:
                            results['errors'].append(f"School '{school_name}' does not exist for class '{row.get('name', '')}'")
                            continue
                        
                        class_name = row.get('name', '')
                        school_class, created = SchoolClass.objects.get_or_create(
                            name=class_name,
                            school=school,
                            defaults={
                                'grade_level': row.get('grade_level', ''),
                                'academic_year': row.get('academic_year', '')
                            }
                        )
                        if created:
                            results['classes_created'] += 1
                    except Exception as e:
                        results['errors'].append(f"Error creating class {row.get('name', '')}: {str(e)}")
        
        # Process Students sheet if it exists
        if 'Students' in excel_data.sheet_names:
            students_df = pd.read_excel(excel_data, 'Students')
            for _, row in students_df.iterrows():
                if pd.notna(row.get('first_name')) and row.get('first_name') != '' and pd.notna(row.get('last_name')) and row.get('last_name') != '':
                    try:
                        # Get the associated school and class
                        school_name = row.get('school_name', '')
                        class_name = row.get('class_name', '')
                        
                        try:
                            school = School.objects.get(name=school_name)
                        except School.DoesNotExist:
                            results['errors'].append(f"School '{school_name}' does not exist for student '{row.get('first_name', '')} {row.get('last_name', '')}'")
                            continue
                        
                        try:
                            school_class = SchoolClass.objects.get(name=class_name, school=school)
                        except SchoolClass.DoesNotExist:
                            results['errors'].append(f"Class '{class_name}' does not exist in school '{school_name}' for student '{row.get('first_name', '')} {row.get('last_name', '')}'")
                            continue
                        
                        # Process date of birth
                        dob = row.get('date_of_birth', None)
                        if pd.notna(dob):
                            dob = pd.to_datetime(dob)
                        else:
                            dob = None
                        
                        student_id = row.get('student_id', '')
                        if pd.isna(student_id):
                            student_id = ''
                            
                        # Check if student already exists
                        student, created = Student.objects.get_or_create(
                            first_name=row.get('first_name', ''),
                            last_name=row.get('last_name', ''),
                            student_id=student_id,
                            school=school,
                            school_class=school_class,
                            defaults={
                                'date_of_birth': dob,
                                'email': row.get('email', ''),
                                'address': row.get('address', ''),
                                'parent_name': row.get('parent_name', ''),
                                'parent_contact': row.get('parent_contact', '')
                            }
                        )
                        if created:
                            results['students_created'] += 1
                    except Exception as e:
                        results['errors'].append(f"Error creating student {row.get('first_name', '')} {row.get('last_name', '')}: {str(e)}")
    
    except Exception as e:
        results['errors'].append(f"Error processing Excel file: {str(e)}")
    
    return Response(results)

def import_page(request):
    """Render the import page"""
    return render(request, 'core/import.html')

@api_view(['POST'])
def add_school(request):
    """Add a single school"""
    serializer = SchoolSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_class(request):
    """Add a single class"""
    # Extract school from data
    school_name = request.data.get('school_name')
    if not school_name:
        return Response({'error': 'school_name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find the school
        school = School.objects.get(name=school_name)
        
        # Prepare the data for the serializer
        class_data = {
            'name': request.data.get('name'),
            'school': school.id,
            'grade_level': request.data.get('grade_level'),
            'academic_year': request.data.get('academic_year')
        }
        
        serializer = SchoolClassSerializer(data=class_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except School.DoesNotExist:
        return Response({'error': f"School '{school_name}' not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def add_student(request):
    """Add a single student"""
    # Extract school and class from data
    school_name = request.data.get('school_name')
    class_name = request.data.get('class_name')
    
    if not school_name:
        return Response({'error': 'school_name is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not class_name:
        return Response({'error': 'class_name is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find the school
        school = School.objects.get(name=school_name)
        
        # Find the class
        try:
            school_class = SchoolClass.objects.get(name=class_name, school=school)
            
            # Prepare the data for the serializer
            student_data = {
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
                'student_id': request.data.get('student_id'),
                'school': school.id,
                'school_class': school_class.id,
                'email': request.data.get('email'),
                'address': request.data.get('address'),
                'parent_name': request.data.get('parent_name'),
                'parent_contact': request.data.get('parent_contact')
            }
            
            # Handle date_of_birth
            dob = request.data.get('date_of_birth')
            if dob:
                try:
                    import datetime
                    if isinstance(dob, str):
                        # Try to parse the date
                        student_data['date_of_birth'] = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
                except Exception as e:
                    return Response({'error': f"Invalid date format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = StudentSerializer(data=student_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except SchoolClass.DoesNotExist:
            return Response({'error': f"Class '{class_name}' not found in school '{school_name}'"}, status=status.HTTP_404_NOT_FOUND)
    
    except School.DoesNotExist:
        return Response({'error': f"School '{school_name}' not found"}, status=status.HTTP_404_NOT_FOUND)