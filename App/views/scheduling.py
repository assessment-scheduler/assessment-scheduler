from flask import Blueprint, redirect, url_for, flash
from ..controllers.auth import staff_required
from ..models.solver_factory import get_solver
from ..controllers import get_active_semester

scheduling_views = Blueprint("scheduling", __name__, template_folder="../templates")

@scheduling_views.route("/schedule", methods=["POST"])
@staff_required
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
    
    return redirect(url_for("assessment_views.get_assessments_page")) 