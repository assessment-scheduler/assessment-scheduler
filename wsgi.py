import click, sys, csv
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from App.database import db, get_migrate
from App.main import create_app
from App.models import Staff, Course

# This commands file allow you to create convenient CLI commands for testing controllers!!

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
  db.drop_all()
  db.init_app(app)
  db.create_all()
  bob = Staff("bob", "test", 300456, "Lecturer", "bob@gmail.com", "bobpass")
  db.session.add(bob)
  db.session.commit()
  print(bob)
  print('database initialized')

# This command retrieves all staff objects
@app.cli.command('get-users')
def get_users():
  staff = Staff.query.all()
  print(staff)
  print('end of staff objects')

# This command assigns courses to staff
@app.cli.command("add-course")
@click.argument(id)
def assign_course(id):
  bob = Staff.query.filter_by(u_ID=id).first()
  
  if not bob:
      print(f'Staff with ID: {id} not found!')
      return
    
  bob.coursesAssigned = ["COMP1601", "COMP1602", "COMP1603"]
  db.session.add(bob)
  db.session.commit()
  print(bob)
  print('courses added')

#load course data from csv file
@app.cli.command("load-courses")
def load_course_data():
  with open('courses.csv') as file: #csv files are used for spreadsheets
    reader = csv.DictReader(file)
    for row in reader: 
      new_course = Course(courseCode=row['courseCode'], courseTitle=row['courseTitle'], description=row['description'], 
        level=row['level'], semester=row['semester'], preReqs=row['preReqs'], p_ID=row['p_ID'],)  #create object
      db.session.add(new_course) 
    db.session.commit() #save all changes OUTSIDE the loop
  print('database intialized')