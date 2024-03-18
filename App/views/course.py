from flask import Blueprint, request, jsonify, render_template
from App.controllers import Staff

course_views = Blueprint('course_views', __name__, template_folder='../templates')

# Gets Course Page
@course_views.route('/courses', methods=['GET'])
def index():
    return render_template('courses.html')

@course_views.route('/get_courses', methods=['GET'])
def get_courses():
    #insert code to pull course list from database
    courses = ['comp1601', 'comp1602', 'comp1603', 'comp1604', 'comp2605', 'comp2603', 'comp2611']
    return courses