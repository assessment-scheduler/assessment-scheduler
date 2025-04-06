import os
import sys
from data_loader import load_all_data
from kris import solve_stage1, solve_stage2, print_schedule, get_timetable_from_db


def run_scheduler(assessment_csv, timetable_csv=None, enrollment_csv=None):

    print("\n===== LOADING DATA =====")
    print(f"Assessment CSV: {assessment_csv}")
    print(f"Timetable CSV: {timetable_csv if timetable_csv else 'Not specified, will try default course_timetable.csv'}")
    print(f"Enrollment CSV: {enrollment_csv if enrollment_csv else 'Not specified'}")
    
    # Load data
    courses, c, phi, timetable_from_csv = load_all_data(assessment_csv, timetable_csv, enrollment_csv)
    
    print("\n===== COURSE DATA =====")
    print(f"Loaded {len(courses)} courses:")
    for i, course in enumerate(courses):
        print(f"  {i}: {course['code']} with {len(course['assessments'])} assessments")
        proctored = sum(1 for a in course['assessments'] if a.get('proctored'))
        print(f"     {proctored} proctored assessments")
    
    # Ensure we have some timetable data - try from database if not from CSV
    if timetable_from_csv:
        print("\n===== TIMETABLE DATA FROM CSV =====")
        print(f"Using timetable data with {len(timetable_from_csv)} entries")
        for (course_idx, day), _ in sorted(timetable_from_csv.items()):
            course_code = courses[course_idx]['code'] if course_idx < len(courses) else "Unknown"
            print(f"  Course {course_code} (idx {course_idx}) has a lecture on day {day}")
        
        timetable = timetable_from_csv
    else:
        print("\n===== TRYING TIMETABLE DATA FROM DATABASE =====")
        try:
            course_codes = [course['code'] for course in courses]
            timetable, code_to_idx = get_timetable_from_db(course_codes)
            print(f"Using timetable data from database with {len(timetable)} entries")
            for (course_idx, day), _ in sorted(timetable.items()):
                course_code = "Unknown"
                for code, idx in code_to_idx.items():
                    if idx == course_idx:
                        course_code = code
                print(f"  Course {course_code} (idx {course_idx}) has a lecture on day {day}")
        except Exception as e:
            print(f"Warning: Could not load timetable data from database: {e}")
            print("No timetable data available - proctored assessments will be scheduled on any weekday")
            timetable = None
    
    # Run optimizer
    print("\n===== RUNNING OPTIMIZER =====")
    K = 84  # 12 weeks * 7 days
    d = 3   # Minimum spacing between overlapping courses
    M = 1000  # Large value for constraints
    
    print(f"Running Stage 1 with {len(courses)} courses...")
    print(f"Timetable data available: {'Yes' if timetable else 'No'}")
    
    U_star, success, _ = solve_stage1(courses, c, K, M, timetable)
    
    if not success:
        print("Failed to find a solution in Stage 1.")
        return
    
    print(f"Running Stage 2 with U* = {U_star}...")
    schedule, Y_star, probability = solve_stage2(courses, c, phi, U_star, K, d, M, timetable)
    
    if schedule:
        print_schedule(schedule, U_star, d, probability)
        
        # Check if proctored assessments are scheduled on timetabled days
        print("\n===== VALIDATION =====")
        validation_issues = []
        for k, week, day, course_code, assessment_info in schedule:
            # Check if this is a proctored assessment
            is_proctored = False
            course_idx = None
            for i, course in enumerate(courses):
                if course['code'] == course_code:
                    assessment_name = assessment_info.split("-")[0]
                    for j_idx, assessment in enumerate(course['assessments']):
                        if assessment['name'] == assessment_name and assessment.get('proctored'):
                            is_proctored = True
                            course_idx = i
                            break
                    break
            
            if is_proctored and timetable:
                day_of_week = day
                if (course_idx, day_of_week) not in timetable:
                    validation_issues.append(
                        f"Warning: Proctored assessment {course_code}-{assessment_info} "
                        f"scheduled on day {day} (K={k}) which is not a timetabled day for this course"
                    )
        
        if validation_issues:
            print("Found validation issues:")
            for issue in validation_issues:
                print(f"  {issue}")
        else:
            print("All proctored assessments are scheduled on timetabled days")
        
        # Save schedule to a file
        save_schedule_to_csv(schedule, 'schedule_output.csv')
        print(f"\nSchedule saved to schedule_output.csv")
    else:
        print("Failed to find a solution in Stage 2.")


def save_schedule_to_csv(schedule, output_file):
    """Save the generated schedule to a CSV file."""
    with open(output_file, 'w') as f:
        f.write("k,week,day,course,assessment\n")
        for k, week, day, course, assessment in schedule:
            f.write(f"{k},{week},{day},{course},{assessment}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_scheduler.py <assessment_csv> [timetable_csv] [enrollment_csv]")
        sys.exit(1)
    
    assessment_csv = sys.argv[1]
    timetable_csv = sys.argv[2] if len(sys.argv) > 2 else None
    enrollment_csv = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check if files exist
    if not os.path.exists(assessment_csv):
        print(f"Error: Assessment file {assessment_csv} not found.")
        sys.exit(1)
    
    if timetable_csv and not os.path.exists(timetable_csv):
        print(f"Error: Timetable file {timetable_csv} not found.")
        sys.exit(1)
    
    if enrollment_csv and not os.path.exists(enrollment_csv):
        print(f"Error: Enrollment file {enrollment_csv} not found.")
        sys.exit(1)
    
    run_scheduler(assessment_csv, timetable_csv, enrollment_csv) 