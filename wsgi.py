import click, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from App.database import db, get_migrate
from App.main import create_app
from App.models import Staff

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

# This command assigns courses to staff
@app.cli.command("add-course")
@click.argument(id, default=300456)
def change_email(id):
  bob = Staff.query.filter_by(lect_ID=id).first()
  if not bob:
      print(f'Staff with ID: {id} not found!')
      return
  bob.coursesAssigned = ["COMP1601", "COMP1602", "COMP1603"]
  db.session.add(bob)
  db.session.commit()
  print(bob)
