from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from App.controllers import course
from App.database import db
from werkzeug.utils import secure_filename
import os, csv
#from flask_jwt_extended import current_user as jwt_current_user
#from flask_jwt_extended import jwt_required

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
@admin_views.route('/uploadcourse', methods=['GET','POST'])
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
                    new_course = course.add_Course(courseCode=row['course code'], courseTitle=row['title'], description=row['description'], level=row['level'], semester=row['sem'], aNum=row['aNum'])
                    # else: ensures courses are available for semester selected
                    #     message = row['course code'] + ' is not offered in Semester 2' + ' ! Please edit Course Listings.'
                    #     return render_template('test.html', message = message)    

            # Return course listings!        
            return render_template('courses.html')     
    