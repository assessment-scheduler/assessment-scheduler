from typing import List, Dict, Any, Optional, Tuple
from datetime import timedelta
from ...models.solver import Solver
from ...models.assessment import Assessment
from ...controllers import (
    get_course_matrix,
    get_phi_matrix,
    print_schedule,
    solve_stage1,
    solve_stage2,
    get_assessment_dictionary_by_course,
    schedule_assessment,
    get_all_course_codes,
    get_all_courses,
    get_active_semester,
    get_semester_duration,
)


class KrisSolver(Solver):
    def compile_course_data(self) -> List[Dict[str, Any]]:
        """Compile unscheduled assessments for all courses."""
        course_assessment_list: list = []
        courses: list = get_all_courses()
        for course in courses:
            assessments: List[Assessment] = get_assessment_dictionary_by_course(course.code)
            if assessments and 'assessments' in assessments:
                filtered_assessments = {
                    'code': assessments['code'],
                    'assessments': [a for a in assessments['assessments'] if not a.get('scheduled')]
                }
                if filtered_assessments['assessments']:
                    course_assessment_list.append(filtered_assessments)
        return course_assessment_list

    def compile_class_matrix(self) -> List[List[int]]:
        """Compile the course overlap matrix."""
        course_list: List[str] = get_all_course_codes()
        matrix: List[List[int]] = get_course_matrix(course_list)
        return matrix

    def schedule_assessments(self, schedule: List[Tuple]) -> bool:
        """Schedule the assessments according to the generated schedule."""
        try:
            if not schedule:
                print("No schedule provided")
                return False
                
            semester = get_active_semester()
            if not semester:
                print("Could not schedule assessments, no active semester")
                return False
                
            success = True
            scheduled_count = 0
            failed_assessments = []
            
            for row in schedule:
                try:
                    k, week, day, code, assessment_info = row
                    name = assessment_info.split("-")[0]
                    
                    schedule_date = semester.start_date + timedelta(days=(k - 1))
                    
                    if schedule_assessment(semester, schedule_date, code, name):
                        scheduled_count += 1
                    else:
                        print(f"Failed to schedule assessment: {code}-{name}")
                        failed_assessments.append(f"{code}-{name}")
                        success = False
                except Exception as row_error:
                    print(f"Error scheduling row {row}: {str(row_error)}")
                    failed_assessments.append(f"{row}")
                    success = False
            
            print(f"Scheduled {scheduled_count} out of {len(schedule)} assessments")
            if failed_assessments:
                print(f"Failed to schedule {len(failed_assessments)} assessments: {', '.join(failed_assessments[:5])}")
                if len(failed_assessments) > 5:
                    print(f"... and {len(failed_assessments) - 5} more")
                    
            return success
            
        except Exception as e:
            import traceback
            print("Error in schedule_assessments:", str(e))
            print("Traceback:", traceback.format_exc())
            return False

    def _run_solver_algorithm(self, courses: List[Dict[str, Any]], matrix: List[List[int]], 
                             phi_matrix: List[List[int]], k: int, d: int, M: int) -> Optional[List[Tuple]]:
        try:
            if not courses:
                print("No unscheduled assessments found")
                return None

            total_assessments = sum(len(course['assessments']) for course in courses)
            print(f"Attempting to schedule {total_assessments} assessments")

            if k <= 0 or d <= 0 or M <= 0:
                print(f"Invalid scheduling parameters: semester duration={k} weeks, max assessments per day={d}, constraint value={M}")
                return None

            print(f"Scheduling constraints: {total_assessments} assessments over {k} weeks, max {d} per day")
            if total_assessments > (k * 5 * d):  # 5 days per week
                print(f"Warning: More assessments ({total_assessments}) than available slots ({k * 5 * d})")

            U_star, stage1_status, stage1_info = solve_stage1(courses, matrix, k, M)
            
            if not stage1_status or U_star is None:
                print(f"Stage 1 failed: Could not find valid assessment spacing.")
                print(f"This usually means either:")
                print(f"1. Too many assessments for the semester duration")
                print(f"2. Conflicting time windows between assessments")
                print(f"3. The constraint value (M={M}) is too restrictive")
                return None
                
            schedule, Y_star, probability = solve_stage2(
                courses, matrix, phi_matrix, U_star, k, d, M
            )
            
            if not schedule:
                print("Stage 2 failed: Could not generate a valid schedule.")
                print(f"This usually means either:")
                print(f"1. Maximum assessments per day (d={d}) is too low")
                print(f"2. Assessment spacing constraints cannot be satisfied")
                return None
                
            print_schedule(schedule, U_star, d, probability)
            return schedule
            
        except Exception as e:
            import traceback
            print("Error in _run_solver_algorithm:", str(e))
            print("Traceback:", traceback.format_exc())
            return None

    def solve(self) -> Optional[List[Tuple]]:
        """
        Implementation of the Solver interface for Kris algorithm.
        Gathers all necessary data and runs the solver.
        
        Returns:
            List of tuples containing (k, week, day, course_code, assessment_info) if successful,
            None otherwise
        """
        try:
            # Get active semester
            semester = get_active_semester()
            if semester is None:
                print("No active semester found")
                return None
                
            # Gather data needed for solver
            courses = self.compile_course_data()
            matrix = self.compile_class_matrix()
            phi_matrix = get_phi_matrix(matrix)
            k = get_semester_duration(semester.id)
            d = semester.max_assessments
            M = semester.constraint_value
            
            # Run solver algorithm
            schedule = self._run_solver_algorithm(courses, matrix, phi_matrix, k, d, M)
            
            # Schedule assessments
            if schedule:
                self.schedule_assessments(schedule)
                
            return schedule
            
        except Exception as e:
            import traceback
            print("Error in solve:", str(e))
            print("Traceback:", traceback.format_exc())
            return None 