from ortools.sat.python import cp_model

# ====================
# Helper Functions
# ====================
def weekend_count(p, d, weekend_days):
    # Count weekend days in interval (p, d] (days p+1 to d).
    count = 0
    start = p + 1 if p >= 0 else 1
    for day in range(start, d + 1):
        day_of_week = ((day - 1) % 7) + 1
        if day_of_week in weekend_days:
            count += 1
    return count

def week_day_to_k(week, day):
    # Convert (week, day) to day index (7 days per week).
    return (week - 1) * 7 + day

# ====================
# Core Solver Function
# ====================
def solve_scheduling_subset(subset, assignments, T, alpha, weekend_days, assignment_info, fixed_assignments_by_id=None):

    model = cp_model.CpModel()
    
    # Create decision variables for each assignment in the subset.
    assign_vars = {}
    for j in subset:
        a_j, b_j, w_j = assignments[j]
        is_proctored = bool(assignment_info[j]['proctored'])
        unique_id = assignment_info[j]['id']
        if fixed_assignments_by_id and unique_id in fixed_assignments_by_id:
            # Assignment already fixed from a previous iteration.
            d_fixed = fixed_assignments_by_id[unique_id]
            for d in range(a_j, b_j + 1):
                var = model.NewBoolVar(f'assign_{j}_{d}')
                if is_proctored:
                    day_of_week = ((d - 1) % 7) + 1
                    if day_of_week in weekend_days:
                        model.Add(var == 0)
                # Force the fixed day.
                model.Add(var == 1 if d == d_fixed else var == 0)
                assign_vars[(j, d)] = var
        else:
            valid_days = []
            for d in range(a_j, b_j + 1):
                var = model.NewBoolVar(f'assign_{j}_{d}')
                if is_proctored:
                    day_of_week = ((d - 1) % 7) + 1
                    if day_of_week in weekend_days:
                        model.Add(var == 0)
                    else:
                        valid_days.append(var)
                else:
                    valid_days.append(var)
                assign_vars[(j, d)] = var
            model.AddExactlyOne(valid_days)
    
    # Compute daily load y[d]: weighted sum of assignments due on day d.
    M_y = sum(assignments[j][2] for j in subset)
    y = {d: model.NewIntVar(0, M_y, f'y_{d}') for d in range(1, T + 1)}
    for d in y:
        model.Add(y[d] == sum(
            assignments[j][2] * assign_vars[(j, d)]
            for j in subset if assignments[j][0] <= d <= assignments[j][1]
        ))
    
    # Used-day indicators z[d].
    z = {d: model.NewBoolVar(f'z_{d}') for d in range(1, T + 1)}
    for d in z:
        model.Add(y[d] >= z[d])
        model.Add(y[d] <= M_y * z[d])
    
    # Predecessor relationship variables u[(p,d)] for p < d.
    u = {}
    for d in range(1, T + 1):
        for p in range(0, d):
            u[(p, d)] = model.NewBoolVar(f'u_{p}_{d}')
    for d in range(1, T + 1):
        model.Add(sum(u[(p, d)] for p in range(0, d)) == z[d])
        for p in range(0, d):
            if p > 0:
                model.Add(u[(p, d)] <= z[p]).OnlyEnforceIf(u[(p, d)])
            for q in range(p + 1, d):
                model.Add(u[(p, d)] + z[q] <= 1)
    
    # Stretch the load by weekends.
    A = {(p, d): (d - p) + alpha * weekend_count(p, d, weekend_days)
         for d in range(1, T + 1) for p in range(0, d)}
    L_var = model.NewIntVar(0, M_y, 'L')
    maxA = max(A.values()) if A else 1
    M_big = M_y * maxA
    for d in range(1, T + 1):
        for p in range(0, d):
            model.Add(y[d] <= L_var * A[(p, d)] + M_big * (1 - u[(p, d)]))
    
    model.Minimize(L_var)
    
    # Solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None
        
    solution = {}
    for j in subset:
        for d in range(assignments[j][0], assignments[j][1] + 1):
            if solver.Value(assign_vars[(j, d)]):
                solution[j] = d
    return solution

# ====================
# Conversion Function for a Course Pair
# ====================
def convert_courses_to_assignments_pair(courses, class_sizes, combo, fixed_ids):
    
    # Convert course data for a pair (combo) of courses.
    # Only include assignments that have not been fixed (as per fixed_ids).
    # Each assignment is given a unique id: (course_index, assessment_index).
    # The weight multiplier is taken from the overlap value between the two courses.
   
    assignments = []
    assignment_info = []
    keys = []  # list of unique ids for assignments in this pair
    for course_idx, course in enumerate(courses):
        if course_idx not in combo:
            continue
        other = (combo - {course_idx}).pop()
        multiplier = class_sizes[course_idx][other]
        for j_idx, assessment in enumerate(course['assessments']):
            unique_id = (course_idx, j_idx)
            if unique_id in fixed_ids:
                continue  # Skip if already scheduled.
            a_j = week_day_to_k(assessment['start_week'], assessment['start_day'])
            b_j = week_day_to_k(assessment['end_week'], assessment['end_day'])
            assignments.append((a_j, b_j, multiplier * assessment['percentage']))
            assignment_info.append({
                'course_index': course_idx,
                'assessment_index': j_idx,
                'assessment_name': assessment['name'],
                'proctored': assessment['proctored'],
                'percentage': assessment['percentage'],
                'multiplier': multiplier,
                'id': unique_id
            })
            keys.append(unique_id)
    return assignments, assignment_info, keys

# ====================
# Main Execution with Iterative Scheduling
# ====================
if __name__ == '__main__':
    # Sample course data (three courses)
    courses = [
        {  # Course C1601
            'assessments': [
                {'name': 'A1', 'percentage': 5,  'start_week': 3, 'start_day': 1,
                 'end_week': 4,  'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 6,  'start_week': 7, 'start_day': 1,
                 'end_week': 8,  'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 6,  'start_week': 10, 'start_day': 1,
                 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1','percentage': 10, 'start_week': 8, 'start_day': 1,
                 'end_week': 9,  'end_day': 7, 'proctored': 1},
                {'name': 'CW2','percentage': 20, 'start_week': 12, 'start_day': 1,
                 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        },
        {  # Course C1602
            'assessments': [
                {'name': 'A1', 'percentage': 5,  'start_week': 3, 'start_day': 1,
                 'end_week': 4,  'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 6,  'start_week': 8, 'start_day': 1,
                 'end_week': 9,  'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 6,  'start_week': 10, 'start_day': 1,
                 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1','percentage': 10, 'start_week': 6, 'start_day': 1,
                 'end_week': 7,  'end_day': 7, 'proctored': 1},
                {'name': 'CW2','percentage': 20, 'start_week': 12, 'start_day': 1,
                 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        },
        {  # Course C1603
            'assessments': [
                {'name': 'A1', 'percentage': 6,  'start_week': 3, 'start_day': 1,
                 'end_week': 4,  'end_day': 7, 'proctored': 0},
                {'name': 'A2', 'percentage': 7,  'start_week': 6, 'start_day': 1,
                 'end_week': 7,  'end_day': 7, 'proctored': 0},
                {'name': 'A3', 'percentage': 7,  'start_week': 10, 'start_day': 1,
                 'end_week': 11, 'end_day': 7, 'proctored': 0},
                {'name': 'CW1','percentage': 10, 'start_week': 8, 'start_day': 1,
                 'end_week': 9,  'end_day': 7, 'proctored': 1},
                {'name': 'CW2','percentage': 20, 'start_week': 12, 'start_day': 1,
                 'end_week': 12, 'end_day': 7, 'proctored': 1},
            ]
        }
    ]
    
    # Overlap matrix: off-diagonals represent overlapping students between courses.
    # For example, 100 students take both C1601 and C1602, 150 take C1602 and C1603,
    # and 0 take both C1601 and C1603.
    class_sizes = [
        [450, 100,   0],
        [100, 350, 150],
        [  0, 150, 300]
    ]
    
    T = 84            # Total days in a 12-week semester
    alpha = 2         # Extra "work" factor for weekend days
    weekend_days = {6, 7}  # Saturday and Sunday
    
    # Define pair combinations.
    course_combinations = [{0, 1}, {1, 2}, {0, 2}]
    # Sort pairs by overlap descending.
    course_combinations = sorted(course_combinations, key=lambda combo: class_sizes[min(combo)][max(combo)], reverse=True)
    
    # Global schedule: keys are (course_index, assessment_index) and values are scheduled day.
    global_schedule = {}
    
    # Process each pair in order.
    for combo in course_combinations:
        overlap = class_sizes[min(combo)][max(combo)]
        combo_names = [f"C160{idx+1}" for idx in sorted(combo)]
        print(f"\nProcessing combination: {combo_names} (Overlap: {overlap} students)")
        # Convert courses to assignments for this pair; skip assignments already fixed.
        assignments, assignment_info, keys = convert_courses_to_assignments_pair(courses, class_sizes, combo, global_schedule)
        if not assignments:
            print("All assignments for this pair already scheduled.")
            continue
        # Use all indices (0 ... len(assignments)-1) as the subset.
        subset = list(range(len(assignments)))
        solution = solve_scheduling_subset(subset, assignments, T, alpha, weekend_days, assignment_info, fixed_assignments_by_id=global_schedule)
        if solution is None:
            print("No feasible schedule found for this pair.")
            continue
        # Update global schedule with newly scheduled assignments.
        for j in solution:
            unique_id = assignment_info[j]['id']
            global_schedule[unique_id] = solution[j]
        # Print the schedule for this pair.
        pair_schedule = []
        for j in solution:
            info = assignment_info[j]
            day = solution[j]
            pair_schedule.append((day, f"{info['assessment_name']} (C160{info['course_index']+1}) : Day {day}"))
        pair_schedule.sort(key=lambda x: x[0])
        print("=== Final Schedule (Sorted by Day) for this pair ===")
        for day, entry in pair_schedule:
            print(entry)
    
    # Finally, collate and print the global schedule (each assignment scheduled only once).
    collated = []
    # To retrieve course name, we use the assignment_info from any pair; here we simply iterate over global_schedule keys.
    for key, day in global_schedule.items():
        course_idx, assmt_idx = key
        # Find assessment name from the course data.
        assessment = courses[course_idx]['assessments'][assmt_idx]
        collated.append((day, f"{assessment['name']} (C160{course_idx+1}) : Day {day}"))
    collated.sort(key=lambda x: x[0])
    print("\n=== Final Collated Schedule (Sorted by Day) Across All Pairs ===")
    for day, entry in collated:
        print(entry)
