from flask import Blueprint, redirect, url_for, flash, request
from ..controllers.auth import staff_required, admin_required
from ..models.solver_factory import get_solver
from ..controllers import get_active_semester
from ..controllers.semester import set_semester_solver
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..controllers.admin import is_admin
from ..controllers.staff import get_staff

scheduling_views = Blueprint("scheduling", __name__, template_folder="../templates")

# Custom decorator that allows either staff or admin access
def staff_or_admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        email = get_jwt_identity()
        if is_admin(email) or get_staff(email):
            return f(*args, **kwargs)
        return redirect('/login')
    return decorated_function

@scheduling_views.route("/schedule", methods=["POST"])
@staff_or_admin_required  # Using our custom decorator instead of staff_required
def get_schedule_action():
    semester = get_active_semester()
    if not semester:
        flash("No active semester found", "error")
        return redirect(url_for("assessment_views.get_assessments_page"))
    
    try:
        solver = get_solver(semester.solver_type)
        schedule = solver.solve()
        
        if schedule:
            flash(f"Successfully scheduled {len(schedule)} assessments", "success")
        else:
            flash("Failed to generate a valid schedule", "error")
            
    except Exception as e:
        flash(f"Error generating schedule: {str(e)}", "error")
    
    # Redirect admin users to admin dashboard, staff to assessments page
    email = get_jwt_identity()
    if is_admin(email):
        return redirect(url_for("admin_views.admin_dashboard"))
    else:
        return redirect(url_for("assessment_views.get_assessments_page"))

@scheduling_views.route("/set_solver/<int:semester_id>", methods=["POST"])
@admin_required
def set_solver_route(semester_id):
    solver_type = request.form.get('solver_type')
    if not solver_type:
        flash("No solver type provided", "error")
        return redirect(url_for("semester_views.update_semester_route", semester_id=semester_id))
    
    if solver_type not in ['kris', 'prof']:
        flash(f"Invalid solver type: {solver_type}", "error")
        return redirect(url_for("semester_views.update_semester_route", semester_id=semester_id))
    
    success = set_semester_solver(semester_id, solver_type)
    if success:
        flash(f"Successfully changed solver to {solver_type}", "success")
    else:
        flash("Failed to change solver type", "error")
    
    return redirect(url_for("semester_views.update_semester_route", semester_id=semester_id))

@scheduling_views.route("/toggle_solver", methods=["POST"])
@admin_required
def toggle_solver():
    """Toggle between 'kris' and 'prof' solvers for the active semester."""
    semester = get_active_semester()
    if not semester:
        flash("No active semester found", "error")
        return redirect(url_for("admin_views.admin_dashboard"))
    
    # Toggle between the two solvers
    new_solver = 'prof' if semester.solver_type == 'kris' else 'kris'
    
    success = set_semester_solver(semester.id, new_solver)
    if success:
        flash(f"Successfully changed solver to {new_solver}", "success")
    else:
        flash("Failed to change solver type", "error")
    
    # Redirect back to the referring page or dashboard
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for("admin_views.admin_dashboard")) 