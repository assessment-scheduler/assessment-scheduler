from ortools.sat.python import cp_model
import pandas as pd
import os
from ..models import CourseTimetable
from .course_timetable import convert_to_timetable_format, get_timetable_entries


def week_day_to_k(week, day):
    return (week - 1) * 7 + day


def load_timetable_data(timetable_file):

    timetable_df = pd.read_csv(timetable_file)
    timetable = {}
    
    # Create a mapping from course_code to course_idx
    course_codes = set(timetable_df['course_code'])
    code_to_idx = {code: idx for idx, code in enumerate(sorted(course_codes))}
    
    # Fill the timetable dictionary
    for _, row in timetable_df.iterrows():
        course_idx = code_to_idx[row['course_code']]
        day_of_week = int(row['day_of_week'])
        timetable[(course_idx, day_of_week)] = True
    
    return timetable, code_to_idx


def get_timetable_from_db(course_codes=None):

    entries = get_timetable_entries()
    
    if course_codes:
        entries = [entry for entry in entries if entry.course_code in course_codes]
        # Create a mapping from course_code to course_idx based on the order in course_codes
        code_to_idx = {code: idx for idx, code in enumerate(course_codes)}
    else:
        # If no course_codes provided, create mapping from all unique course codes
        unique_codes = sorted(set(entry.course_code for entry in entries))
        code_to_idx = {code: idx for idx, code in enumerate(unique_codes)}
    
    # Convert entries to timetable format using the correct course indices
    timetable = {}
    for entry in entries:
        course_idx = code_to_idx[entry.course_code]
        day_of_week = entry.day_of_week
        timetable[(course_idx, day_of_week)] = True
    
    return timetable, code_to_idx


def build_stage1_model(courses, c, K, M, timetable):
    model = cp_model.CpModel()
    x = {}
    
    # IMPORTANT: Create a direct mapping of course codes to indices used in this function
    course_code_to_idx = {course['code']: i for i, course in enumerate(courses)}
    print(f"DEBUG: Course index mapping in build_stage1_model:")
    for code, idx in course_code_to_idx.items():
        print(f"DEBUG:   {code} -> {idx}")
    
    # Create x variables for Stage 1
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            for k in range(start_k, end_k + 1):
                if 1 <= k <= K:
                    x[(k, i, j_idx)] = model.NewBoolVar(f'x1_{k}_{i}_{j_idx}')
    
    # Each assessment scheduled exactly once
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            possible_ks = [k for k in range(start_k, end_k + 1) if 1 <= k <= K]
            model.AddExactlyOne([x[(k, i, j_idx)] for k in possible_ks])
    
    # Handle proctored assessments
    for i, course in enumerate(courses):
        course_code = course['code']
        for j_idx, assessment in enumerate(course['assessments']):
            if assessment.get('proctored', False):
                print(f"DEBUG: Processing proctored assessment {course_code}-{assessment['name']}")
                
                for k in range(1, K + 1):
                    x_key = (k, i, j_idx)
                    if x_key not in x:
                        continue
                    
                    day_of_week = ((k - 1) % 7) + 1
                    
                    # No assessments on weekends
                    if day_of_week > 5:  # Saturday or Sunday
                        model.Add(x[x_key] == 0)
                        print(f"DEBUG: {course_code} (idx {i}): Disallowing {assessment['name']} on k={k} (day {day_of_week}) - Weekend")
                        continue
                    
                    # Check timetable constraints
                    if timetable is not None:
                        timetable_key = (i, day_of_week)
                        has_lecture = timetable.get(timetable_key, False)
                        
                        if has_lecture:
                            print(f"DEBUG: {course_code} (idx {i}): Allowing {assessment['name']} on k={k} (day {day_of_week}) - Has lecture")
                        else:
                            model.Add(x[x_key] == 0)
                            print(f"DEBUG: {course_code} (idx {i}): Disallowing {assessment['name']} on k={k} (day {day_of_week}) - No lecture")
                            
                        # Additional debug output to verify
                        allowed_days = [d for d in range(1, 6) if timetable.get((i, d), False)]
                        print(f"DEBUG: {course_code} (idx {i}) allowed lecture days: {allowed_days}")
    
    # Each course and time has at most one assessment
    course_time_vars = {}
    for (k, i, j_idx), var in x.items():
        key = (k, i)
        course_time_vars.setdefault(key, []).append(var)
    for key, vars_list in course_time_vars.items():
        model.Add(sum(vars_list) <= 1)
    # Define U as the maximum load
    U = model.NewIntVar(0, 10000000, 'U')
    # Weight matrix from assessments' percentages
    w = [[a['percentage'] for a in course['assessments']] for course in courses]
    # Ensure load does not exceed U on any day for each course combination
    for k in range(1, K + 1):
        for i in range(len(courses)):
            terms = []
            for i_prime in range(len(courses)):
                for j_idx in range(len(courses[i_prime]['assessments'])):
                    x_key = (k, i_prime, j_idx)
                    if x_key in x:
                        coeff = c[i][i_prime] * w[i_prime][j_idx]
                        terms.append(x[x_key] * coeff)
            if terms:
                model.Add(sum(terms) <= U)
    # Minimize U
    model.Minimize(U)
    return model, x, U


def solve_stage1(courses, c, K, M, timetable=None):
    model, x, U = build_stage1_model(courses, c, K, M, timetable)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:
        U_star = solver.Value(U)
        print(f"Stage 1 solved with U* = {U_star}")
        return U_star, True, x
    else:
        print("Stage 1 failed to find an optimal solution.")
        return None, False, None

def build_stage2_model(courses, c, phi, U_star, K, d, M, timetable=None):
    model = cp_model.CpModel()
    x = {}
    print(timetable)
    # Create x variables for Stage 2
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            for k in range(start_k, end_k + 1):
                if 1 <= k <= K:
                    x[(k, i, j_idx)] = model.NewBoolVar(f'x2_{k}_{i}_{j_idx}')
    # Each assessment scheduled exactly once
    for i, course in enumerate(courses):
        for j_idx, assessment in enumerate(course['assessments']):
            start_k = week_day_to_k(assessment['start_week'], assessment['start_day'])
            end_k = week_day_to_k(assessment['end_week'], assessment['end_day'])
            possible_ks = [k for k in range(start_k, end_k + 1) if 1 <= k <= K]
            model.AddExactlyOne([x[(k, i, j_idx)] for k in possible_ks])
    # Handle proctored assessments
    for (k, i, j_idx), var in x.items():
        assessment = courses[i]['assessments'][j_idx]
        if assessment['proctored']:
            day_of_week = (k - 1) % 7 + 1
            
            # If weekend, assessment can't be scheduled
            if day_of_week > 5:
                model.Add(var == 0)
            
            # If timetable data is provided, ensure proctored assessments only on lecture days
            if timetable is not None:
                # If day is not a lecture day for this course, assessment can't be scheduled
                if not timetable.get((i, day_of_week), False):
                    model.Add(var == 0)
    # Each course and time has at most one assessment
    course_time_vars = {}
    for (k, i, j_idx), var in x.items():
        key = (k, i)
        course_time_vars.setdefault(key, []).append(var)
    for key, vars_list in course_time_vars.items():
        model.Add(sum(vars_list) <= 1)
    # Ensure load does not exceed U*
    w = [[a['percentage'] for a in course['assessments']] for course in courses]
    for k in range(1, K + 1):
        for i in range(len(courses)):
            terms = []
            for i_prime in range(len(courses)):
                for j_idx in range(len(courses[i_prime]['assessments'])):
                    x_key = (k, i_prime, j_idx)
                    if x_key in x:
                        coeff = c[i][i_prime] * w[i_prime][j_idx]
                        terms.append(x[x_key] * coeff)
            if terms:
                model.Add(sum(terms) <= U_star)
    # Enforce spacing between overlapping courses
    for i in range(len(courses)):
        for i_prime in range(len(courses)):
            if i >= i_prime or phi[i][i_prime] == 0:
                continue  # Skip duplicates and non-overlapping courses
            for j_idx in range(len(courses[i]['assessments'])):
                for j_prime_idx in range(len(courses[i_prime]['assessments'])):
                    for k in range(1, K - d + 1):
                        var1 = x.get((k, i, j_idx), None)
                        var2 = x.get((k + d + 1, i_prime, j_prime_idx), None)
                        if var1 is not None and var2 is not None:
                            model.Add(var1 + var2 <= 1)
    # Create y variables for time windows
    y = {k: model.NewBoolVar(f'y_{k}') for k in range(1, K - d + 1)}
    # Add window constraints for y variables
    for k in range(1, K - d + 1):
        window_assessments = []
        for k_prime in range(k, k + d + 1):
            if k_prime > K:
                continue
            for i_prime in range(len(courses)):
                for j_idx in range(len(courses[i_prime]['assessments'])):
                    x_key = (k_prime, i_prime, j_idx)
                    if x_key in x:
                        window_assessments.append(x[x_key])
        model.Add(sum(window_assessments) <= 1).OnlyEnforceIf(y[k])
        model.Add(sum(window_assessments) >= 2).OnlyEnforceIf(y[k].Not())
    # Maximize Y*
    model.Maximize(sum(y[k] for k in range(1, K - d + 1)))
    return model, x, y


def solve_stage2(courses, c, phi, U_star, K, d, M, timetable=None):
    model, x, y = build_stage2_model(courses, c, phi, U_star, K, d, M, timetable)
    solver = cp_model.CpSolver()
    from flask import current_app
    solver.parameters.max_time_in_seconds = current_app.config['SOLVER_TIMEOUT']
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:
        Y_star = sum(solver.Value(y[k]) for k in range(1, K - d + 1))
        probability = Y_star / (K - d)
        print(f"\nStage 2 solved with Y* = {Y_star}")
        print(f"Probability: {probability:.3f}")
        schedule = []
        for (k, i, j_idx), var in x.items():
            if solver.Value(var):
                assessment = courses[i]['assessments'][j_idx]
                week = (k - 1) // 7 + 1
                day_of_week = (k - 1) % 7 + 1
                course_name = courses[i]['code']
                assessment_name = f"{assessment['name']}-({assessment['percentage']})"
                schedule.append((k, week, day_of_week, course_name, assessment_name))
        schedule.sort(key=lambda x: x[0])
        return schedule, Y_star, probability
    else:
        print("Stage 2 failed to find an optimal solution.")
        return None, None, None


def print_schedule(schedule, U_star, d, probability):
    print(f"\nStage 2 Schedule:")
    print(f"U* = {U_star}, d = {d}, Y*/K-d = {probability:.3f}")
    print("-" * 55)
    print(f"| {'K':<2} | {'WK':<3} | {'DAY':<4} | {'Assessment':<35} |")
    print("-" * 55)
    for entry in schedule:
        k, week, day, course, assessment = entry
        print(f"| {k:<2} | {week:<3} | {day:<4} | {course}-{assessment:<30} |")
    print("-" * 55)

# # Example usage
# def main():
    
#     # Get course codes for timetable lookup
#     course_codes = [course['code'] for course in courses]

#     # Class sizes matrix
#     c = [
#         [450, 100, 0],
#         [100, 350, 150],
#         [0, 150, 300]
#     ]
#     # Phi matrix (1 if at least one student is registered for both courses)
#     phi = [[1 if ci > 0 else 0 for ci in row] for row in c]

#     K = 84  # 12 weeks * 7 days
#     d = 3   # Minimum spacing between overlapping courses
#     M = 1000  # A large value for constraints

#     # Load timetable data - first try from DB, fall back to CSV
#     try:
#         timetable, _ = get_timetable_from_db(course_codes)
#         print(f"Loaded timetable data from database with {len(timetable)} entries.")
#     except Exception as e:
#         print(f"Warning: Could not load timetable data from database: {e}")
#         try:
#             timetable_file = os.path.join('App', 'static', 'course_timetable.csv')
#             timetable, _ = load_timetable_data(timetable_file)
#             print(f"Loaded timetable data from CSV with {len(timetable)} entries.")
#         except Exception as e:
#             print(f"Warning: Could not load timetable data from CSV: {e}")
#             timetable = None

#     U_star, _, _ = solve_stage1(courses, c, K, M, timetable)
#     schedule, Y_star, probability = solve_stage2(courses, c, phi, U_star, K, d, M, timetable)
#     print_schedule(schedule, U_star, d, probability)


# if __name__ == '__main__':
#     main()