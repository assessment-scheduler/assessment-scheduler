from flask import Blueprint, render_template, request, jsonify, flash
from App.models.kris import solve_stage1, solve_stage2
from App.database import db
from App.models.course import Course
from App.models.class_size import ClassSize
from App.models.importer import load_class_sizes
import json
import csv
import io

scheduling = Blueprint('scheduling', __name__)

@scheduling.route('/kris', methods=['GET'])
def kris_form():
    default_courses = [
        {
            'name': 'C1601',
            'assessments': [
                {'name': 'A1', 'percentage': 5, 'start_week': 3, 'start_day': 1, 'end_week': 4, 'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 6, 'start_week': 7, 'start_day': 1, 'end_week': 8, 'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 6, 'start_week': 10, 'start_day': 1, 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1', 'percentage': 10, 'start_week': 8, 'start_day': 1, 'end_week': 9, 'end_day': 7, 'proctored': 1},
                {'name': 'CW2', 'percentage': 20, 'start_week': 12, 'start_day': 1, 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        },
        {
            'name': 'C1602',
            'assessments': [
                {'name': 'A1', 'percentage': 5, 'start_week': 3, 'start_day': 1, 'end_week': 4, 'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 6, 'start_week': 8, 'start_day': 1, 'end_week': 9, 'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 6, 'start_week': 10, 'start_day': 1, 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1', 'percentage': 10, 'start_week': 6, 'start_day': 1, 'end_week': 7, 'end_day': 7, 'proctored': 1},
                {'name': 'CW2', 'percentage': 20, 'start_week': 12, 'start_day': 1, 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        },
        {
            'name': 'C1603',
            'assessments': [
                {'name': 'A1', 'percentage': 6, 'start_week': 3, 'start_day': 1, 'end_week': 4, 'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 7, 'start_week': 6, 'start_day': 1, 'end_week': 7, 'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 7, 'start_week': 10, 'start_day': 1, 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1', 'percentage': 10, 'start_week': 8, 'start_day': 1, 'end_week': 9, 'end_day': 7, 'proctored': 1},
                {'name': 'CW2', 'percentage': 20, 'start_week': 12, 'start_day': 1, 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        }
    ]
    
    default_c = [
        [450, 100, 0],
        [100, 350, 150],
        [0, 150, 300]
    ]
    
    return render_template('kris_form.html', 
                         courses=default_courses,
                         class_sizes=default_c,
                         K=84,
                         d=3,
                         M=1000)

@scheduling.route('/kris/solve', methods=['POST'])
def solve_kris():
    data = request.json
    courses = data['courses']
    c = data['class_sizes']
    K = data['K']
    d = data['d']
    M = data['M']
    
    # Generate phi matrix from class sizes
    phi = [[1 if ci > 0 else 0 for ci in row] for row in c]
    
    try:
        U_star, _, _ = solve_stage1(courses, c, K, M)
        schedule, Y_star, probability = solve_stage2(courses, c, phi, U_star, K, d, M)
        
        # Format schedule for display
        formatted_schedule = []
        for k, week, day, course, assessment in schedule:
            formatted_schedule.append({
                'k': k,
                'week': week,
                'day': day,
                'course': course,
                'assessment': assessment
            })
            
        return jsonify({
            'success': True,
            'schedule': formatted_schedule,
            'U_star': U_star,
            'Y_star': Y_star,
            'probability': probability
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@scheduling.route('/matrix/upload', methods=['GET'])
def matrix_upload_form():
    return render_template('matrix_upload.html')

@scheduling.route('/api/class-matrix/update', methods=['POST'])
def update_class_matrix():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided', 'success': False}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected', 'success': False}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV', 'success': False}), 400
    
    try:
        # Convert file to string IO for processing
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        courses_dict = {course.course_code: course for course in Course.query.all()}
        
        # Clear existing class sizes for courses in the CSV
        reader = csv.DictReader(stream)
        affected_courses = set()
        for row in reader:
            if row['course_code'] in courses_dict and row['other_course_code'] in courses_dict:
                affected_courses.add(row['course_code'])
        
        for course_code in affected_courses:
            ClassSize.query.filter_by(course_id=courses_dict[course_code].id).delete()
        
        # Reset file pointer and load new data
        stream.seek(0)
        stream = io.StringIO(stream.getvalue())  # Create a new stream since file was consumed
        load_class_sizes(stream, courses_dict)
        
        return jsonify({'message': 'Matrix updated successfully', 'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@scheduling.route('/matrix', methods=['GET'])
def display_matrix():
    courses = Course.query.all()
    print(f"Found {len(courses)} courses")  # Debug print
    
    if not courses:
        flash('No courses found in the database.')
        return render_template('matrix.html', courses=[], class_sizes=[])
    
    # Initialize empty matrix
    n = len(courses)
    class_sizes = [[0 for _ in range(n)] for _ in range(n)]
    
    # Fill in the matrix with actual class sizes
    for i, course in enumerate(courses):
        print(f"Processing course {course.course_code}")  # Debug print
        for class_size in course.class_sizes:
            # Find index of the other course
            other_course_idx = next(
                (idx for idx, c in enumerate(courses) if c.id == class_size.other_course_id),
                None
            )
            if other_course_idx is not None:
                class_sizes[i][other_course_idx] = class_size.size
    
    return render_template('matrix.html', courses=courses, class_sizes=class_sizes)