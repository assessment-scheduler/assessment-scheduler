from flask import Blueprint, request, jsonify, render_template
from App.controllers import Staff

course_views = Blueprint('course_views', __name__, template_folder='../templates')

# Gets Course Page
@course_views.route('/courses', methods=['GET'])
def index():
    return render_template('courses.html')