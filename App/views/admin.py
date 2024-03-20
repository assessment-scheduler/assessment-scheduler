from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from App.controllers import Course
from App.database import db
from werkzeug.utils import secure_filename
import os, csv
#from flask_jwt_extended import current_user as jwt_current_user
#from flask_jwt_extended import jwt_required

from App.controllers.course import (
    add_Course,
    list_Courses,
    get_course,
    delete_Course
)

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')
 
# Ensures that variables are set just once on application startup!
@admin_views.before_app_first_request
def set_variables():
    global semBegins 
    global semEnds
    global semChoice

# Gets Semester Details Page
@admin_views.route('/semester', methods=['GET'])
def get_upload_page():
    return render_template('semester.html')

# Gets Course Listings Page
@admin_views.route('/coursesList', methods=['GET'])
def index():
    return render_template('courses.html')    

# Retrieves semester details and stores it in global variables 
@admin_views.route('/newSemester', methods=['POST'])
def new_semester_action():
    if request.method == 'POST':
        semBegins = request.form.get('teachingBegins')
        semEnds = request.form.get('teachingEnds')
        semChoice = request.form.get('semester')
        
        # Return course upload page to upload cvs file for courses offered that semester
        return render_template('test.html')  
               
# Uploads course details file and extracts data
@admin_views.route('/uploadcourse', methods=['POST'])
def upload_course_file():
    if request.method == 'POST': 
        file = request.files['file'] 

        # Check if file is present
        if (file.filename == ''):
            message = 'No file selected!' 
            return render_template('test.html', message = message) 
        else:
            # Secure filename
            filename = secure_filename(file.filename)
        
            # Save file to uploads folder
            file.save(os.path.join('App/uploads', filename)) 
            
            # Retrieves course details from file and stores it in database ie. store course info 
            fpath = 'App/uploads/' + filename
            with open(fpath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    #create object
                    course = add_Course(courseCode=row['course code'], courseTitle=row['title'], description=row['description'], level=int(row['level']), semester=int(row['sem']), aNum=int(row['aNum']))

            # Redirect to view course listings!   
            return redirect(url_for('admin_views.get_courses'))    
            # return jsonify({"message": "Courses file successfully uploaded."}), 200 # for postman   


# Pull course list from database
@admin_views.route('/get_courses', methods=['GET'])
def get_courses():
    courses = list_Courses()
    return render_template('courses.html', courses=courses)
    # return jsonify([course.to_json() for course in courses]), 200 #for postman

# Gets Add Course Page
@admin_views.route('/newCourse', methods=['GET'])
def get_new_course():
    return render_template('addCourse.html')  

# Retrieves course info and stores it in database ie. add new course
@admin_views.route('/addNewCourse', methods=['POST'])
def add_course_action():
    if request.method == 'POST':
        courseCode = request.form.get('course_code')
        title = request.form.get('title')
        description = request.form.get('description')
        level = request.form.get('level')
        semester = request.form.get('semester')
        numAssessments = request.form.get('numAssessments')
         
        course = add_Course(courseCode,title,description,level,semester,numAssessments)

        # Redirect to view course listings!    
        #return redirect(url_for('admin_views.get_courses')) 
        return jsonify({"message":f" {courseCode} successfully added to course listings."}), 200  #for postman

# Get selectec course
# @admin_views.route('/selectedCourse', methods=['GET'])
# def get_selected_course():


# Gets Update Course Page
@admin_views.route('/modifyCourse/<string:courseCode>', methods=['GET'])
def get_update_course(courseCode):
    course = get_course(courseCode) # Gets selected course
    # return jsonify({"message":f" {course} selected to modify."}), 200 #for postman
    return render_template('updateCourse.html', course=course)  

# Selects new course details and updates existing course in database
@admin_views.route('/updateCourse', methods=['GET'])
def get_modify_course():
    # courseCode = request.args.get['data']

    # course={
    #     "Code":"COMP1601",
    #     "Title":"Computer Programming I",
    #     "Description":"This course uses an appropriate programming language as a tool to teach fundamental programming concepts. The main concepts covered are sequence, selection and repetition logic, character and string manipulation, function, and a basic introduction to arrays and their applications.",
    #     "Level":"1",
    #     "Semester":["1","3"],
    #     "aNum":"3",
    #     "Programme":"IT (Special), Computer Science (Major)"
    # }

    # Redirect to view course listings! 
    return redirect(url_for('admin_views.get_courses'))   

# Selects course and removes it from database
@admin_views.route("/deleteCourse/<string:courseCode>", methods=["GET", "POST", "DELETE"])
def delete_course_action(courseCode):
    course = get_course(courseCode) # Gets selected course
    delete_Course(course)

    # Redirect to view course listings!   
    return redirect(url_for('admin_views.get_courses'))    
    # return jsonify({"message":f" {courseCode} successfully delete from course listings."}), 200 # for postman

