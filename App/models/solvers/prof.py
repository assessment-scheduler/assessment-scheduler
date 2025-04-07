from typing import List, Dict, Any, Optional, Tuple
from ortools.sat.python import cp_model
from ...models.solver import Solver
from datetime import timedelta
from ...controllers import (
    get_course_matrix,
    get_phi_matrix,
    get_all_course_codes,
    get_all_courses,
    get_active_semester,
    get_semester_duration,
    get_assessment_dictionary_by_course,
    schedule_assessment,
)

class ProfSolver(Solver):
    def __init__(self):
        self.weekend_days = {6, 7}  # Saturday and Sunday
        self.alpha = 2  # Extra "work" factor for weekend days

    def _weekend_count(self, p, d, weekend_days):
        count = 0
        start = p + 1 if p >= 0 else 1
        for day in range(start, d + 1):
            day_of_week = ((day - 1) % 7) + 1
            if day_of_week in weekend_days:
                count += 1
        return count

    def _week_day_to_k(self, week, day):
        return (week - 1) * 7 + day

    def _solve_scheduling_subset(self, subset, assignments, T, alpha, weekend_days, 
                               assignment_info, fixed_assignments_by_id=None, timetable=None):
       
        model = cp_model.CpModel()
        
        # Create decision variables for each assignment in the subset.
        assign_vars = {}
        for j in subset:
            a_j, b_j, w_j = assignments[j]
            is_proctored = bool(assignment_info[j]['proctored'])
            unique_id = assignment_info[j]['id']
            course_index = assignment_info[j]['course_index']
            
            if fixed_assignments_by_id and unique_id in fixed_assignments_by_id:
                # Assignment already fixed from a previous iteration.
                d_fixed = fixed_assignments_by_id[unique_id]
                for d in range(a_j, b_j + 1):
                    var = model.NewBoolVar(f'assign_{j}_{d}')
                    if is_proctored:
                        day_of_week = ((d - 1) % 7) + 1
                        if day_of_week in weekend_days:
                            model.Add(var == 0)
                            
                        # For proctored assessments, check if day matches timetable
                        if timetable and day_of_week <= 5:  # Weekday
                            # Only allow scheduling on timetable days
                            if (course_index, day_of_week) not in timetable:
                                model.Add(var == 0)
                    
                    # Force the fixed day.
                    model.Add(var == 1 if d == d_fixed else var == 0)
                    assign_vars[(j, d)] = var
            else:
                valid_days = []
                for d in range(a_j, b_j + 1):
                    var = model.NewBoolVar(f'assign_{j}_{d}')
                    day_of_week = ((d - 1) % 7) + 1
                    
                    if is_proctored:
                        # Proctored assessments can't be scheduled on weekends
                        if day_of_week in weekend_days:
                            model.Add(var == 0)
                        else:
                            # For proctored assessments, check if day matches timetable
                            if timetable and (course_index, day_of_week) in timetable:
                                valid_days.append(var)
                            elif not timetable:  # If no timetable data, allow all weekdays
                                valid_days.append(var)
                            else:
                                model.Add(var == 0)  # Can't schedule on days not in timetable
                    else:
                        valid_days.append(var)  # Non-proctored assessments can be any day
                        
                    assign_vars[(j, d)] = var
                
                if valid_days:  # Only add constraint if there are valid days
                    model.AddExactlyOne(valid_days)
                else:
                    # No valid days found, this problem is infeasible
                    return None
        
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
        A = {(p, d): (d - p) + alpha * self._weekend_count(p, d, weekend_days)
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
                if (j, d) in assign_vars and solver.Value(assign_vars[(j, d)]):
                    solution[j] = d
        return solution

    def _convert_courses_to_assignments_pair(self, courses, class_sizes, combo, fixed_ids):
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
                a_j = self._week_day_to_k(assessment['start_week'], assessment['start_day'])
                b_j = self._week_day_to_k(assessment['end_week'], assessment['end_day'])
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

    def _prepare_course_data(self):
        
        semester = get_active_semester()
        if not semester:
            print("No active semester found")
            return None, None
            
        courses = []
        all_course_codes = []
        
        for assignment in semester.course_assignments:
            course_code = assignment.course_code
            course_data = get_assessment_dictionary_by_course(course_code)
            if not course_data or not course_data.get('assessments'):
                continue
                
            all_course_codes.append(course_code)
            course_obj = {
                'code': course_code,
                'assessments': []
            }
            
            for assessment in course_data['assessments']:
                if assessment.get('scheduled'):
                    continue  # Skip already scheduled assessments
                    
                # Use the actual values from the database for each assessment
                assessment_obj = {
                    'name': assessment['name'],
                    'percentage': assessment['percentage'],
                    'proctored': assessment['proctored'],
                    'start_week': assessment.get('start_week', 1),  # Use actual value with fallback
                    'start_day': assessment.get('start_day', 1),
                    'end_week': assessment.get('end_week', semester.max_assessments),
                    'end_day': assessment.get('end_day', 5)
                }
                
                course_obj['assessments'].append(assessment_obj)
                
            if course_obj['assessments']:
                courses.append(course_obj)
                
        return courses, all_course_codes

    def _build_matrix(self, course_codes) -> List[List[int]]:
        from ...controllers.courseoverlap import get_course_matrix, verify_matrix_consistency
        
        # Use debug=True to enable debugging output
        matrix = get_course_matrix(course_codes, debug=True)
        
        # Verify matrix consistency with the database
        matrix = verify_matrix_consistency(matrix, course_codes, debug=True)
        
        return matrix

    def schedule_assessments(self, schedule, courses):
        if not schedule:
            return False
            
        semester = get_active_semester()
        if not semester:
            return False
            
        try:
            for idx, day in schedule.items():
                course_idx, assessment_idx = idx
                course = courses[course_idx]
                course_code = course['code']
                assessment_name = course['assessments'][assessment_idx]['name']
                
                # Calculate date based on day number
                scheduled_date = semester.start_date + timedelta(days=day-1)
                
                result = schedule_assessment(
                    semester,
                    scheduled_date,
                    course_code, 
                    assessment_name
                )
                
                if not result:
                    print(f"Failed to schedule {course_code} - {assessment_name}")
                    
            return True
        except Exception as e:
            import traceback
            print(f"Error scheduling assessments: {e}")
            print(traceback.format_exc())
            return False

    def solve(self) -> Optional[List[Tuple]]:
        try:
            # Prepare course data
            courses, course_codes = self._prepare_course_data()
            if not courses:
                print("No courses with unscheduled assessments found")
                return None
                
            # Build the course overlap matrix
            matrix = self._build_matrix(course_codes)
            if not matrix:
                print("Failed to generate course matrix")
                return None
                
            # Define the semester duration
            semester = get_active_semester()
            if not semester:
                return None
                
            T = get_semester_duration(semester.id)
            
            # Read timetable data from CSV
            timetable = {}
            try:
                import csv
                import os
                csv_data = {}
                
                timetable_path = os.path.join('App', 'uploads', 'course_timetable.csv')
                if os.path.exists(timetable_path):
                    print(f"Reading timetable from {timetable_path}")
                    with open(timetable_path, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            course_code = row['CourseID']
                            days_str = row['Days']
                            day_numbers = []
                            
                            # Parse day strings into day numbers
                            for day in days_str.split(';'):
                                day_mapping = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5}
                                day_number = day_mapping.get(day.strip(), None)
                                if day_number:
                                    day_numbers.append(day_number)
                                    
                            csv_data[course_code] = day_numbers
                    
                    # Create timetable dictionary mapping course index to days
                    for course_idx, course in enumerate(courses):
                        course_code = course['code']
                        if course_code in csv_data:
                            for day in csv_data[course_code]:
                                timetable[(course_idx, day)] = True
                                print(f"Added timetable entry: {course_code} (idx {course_idx}) on day {day}")
                        else:
                            print(f"WARNING: No timetable data for course {course_code}")
                    
                    print(f"Created timetable with {len(timetable)} entries")
                else:
                    print(f"Timetable file not found at {timetable_path}")
            except Exception as e:
                import traceback
                print(f"Error reading timetable: {e}")
                print(traceback.format_exc())
                # Continue without timetable constraints
                timetable = {}
            
            # Define course combinations
            course_combinations = []
            for i in range(len(courses)):
                for j in range(i+1, len(courses)):
                    if matrix[i][j] > 0:  # Only consider pairs with overlapping students
                        course_combinations.append({i, j})
                        
            # Sort pairs by overlap descending
            course_combinations = sorted(
                course_combinations, 
                key=lambda combo: matrix[min(combo)][max(combo)], 
                reverse=True
            )
            
            # Global schedule: keys are (course_index, assessment_index) and values are scheduled day
            global_schedule = {}
            
            # Process each pair in order
            print(f"Processing {len(course_combinations)} course pairs")
            for combo in course_combinations:
                overlap = matrix[min(combo)][max(combo)]
                combo_names = [courses[idx]['code'] for idx in sorted(combo)]
                print(f"Processing combination: {combo_names} (Overlap: {overlap} students)")
                
                # Convert courses to assignments for this pair; skip assignments already fixed
                assignments, assignment_info, keys = self._convert_courses_to_assignments_pair(
                    courses, matrix, combo, global_schedule
                )
                
                if not assignments:
                    print("All assignments for this pair already scheduled.")
                    continue
                    
                # Use all indices (0 ... len(assignments)-1) as the subset
                subset = list(range(len(assignments)))
                solution = self._solve_scheduling_subset(
                    subset, assignments, T, self.alpha, self.weekend_days, 
                    assignment_info, fixed_assignments_by_id=global_schedule, 
                    timetable=timetable  # Pass timetable to the solver
                )
                
                if solution is None:
                    print("No feasible schedule found for this pair.")
                    continue
                    
                # Update global schedule with newly scheduled assignments
                for j in solution:
                    unique_id = assignment_info[j]['id']
                    global_schedule[unique_id] = solution[j]
                    
                # Print the schedule for this pair
                print(f"Scheduled {len(solution)} assignments for this pair")
            
            # Finally, schedule the assessments in the database
            if not global_schedule:
                print("No assignments could be scheduled")
                return None
                
            print(f"Final schedule has {len(global_schedule)} assignments")
            self.schedule_assessments(global_schedule, courses)
            
            # Prepare the return value in the expected format
            # The Solver interface expects a list of tuples: (k, week, day, course_code, assessment_name)
            result = []
            for (course_idx, assessment_idx), day in global_schedule.items():
                course = courses[course_idx]
                course_code = course['code']
                assessment_name = course['assessments'][assessment_idx]['name']
                week = (day - 1) // 7 + 1
                day_of_week = ((day - 1) % 7) + 1
                result.append((day, week, day_of_week, course_code, assessment_name))
                
            return result
            
        except Exception as e:
            import traceback
            print(f"Error in Prof solver: {e}")
            print(traceback.format_exc())
            return None 