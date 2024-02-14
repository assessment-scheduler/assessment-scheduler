from flask import Blueprint, request, jsonify, renderTemplate
from App.database import db
from App.models.lecturer import register
from flask_jwt_extended import current_user as jwt_current_user
from flask_jwt_extended import jwt_required

lect_views = Blueprint('lect_views', __name__, template_folder='../templates')

@lect_views.route('/register', methods=['POST'])
def newLect():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    pwd = request.form['password']

    if (firstName == '' or lastName == '' or email == '' or pwd == ''):
        renderTemplate('signup.html', message = 'Please enter required fields.')

    #Check if email is already used by another lecturer ie. lecturer already registered
    if db.session.query(Lecturer).filter(Lecturer.email == email).count == 0:
        register(self, fName, lName, email, pwd)
        return renderTemplate('index.html')    