from flask import Blueprint, render_template, redirect, url_for, flash
from ..database import db
from ..controllers import initialize
from ..controllers.auth import admin_required

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@index_views.route('/init', methods=['GET'])
@admin_required
def init():
    try:
        initialize()
        flash("Database initialized successfully", "success")
    except Exception as e:
        flash(f"Error initializing database: {str(e)}", "error")
    
    return redirect(url_for('admin_views.admin_dashboard'))

@index_views.route('/init-page', methods=['GET'])
@admin_required
def init_page():
    return render_template('database_init.html')
