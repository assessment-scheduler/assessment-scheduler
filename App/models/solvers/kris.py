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
        
        semester = get_active_semester()
        if not semester:
            print("No active semester found")
            return []
            
        courses = semester.courses
        print(f"Found {len(courses)} courses in active semester")
        
        total_assessments = 0
        scheduled_assessments = 0
        
        for course in courses:
            if course is None:
                print("Warning: Found None course in semester courses list, skipping")
                continue
                
            try:
                print(f"Processing course: {course.code}")
                assessments: List[Assessment] = get_assessment_dictionary_by_course(course.code)
                
                if not assessments:
                    print(f"  No assessments found for course {course.code}")
                    continue
                    
                if 'assessments' not in assessments:
                    print(f"  No assessments list found for course {course.code}")
                    continue
                
                all_course_assessments = assessments.get('assessments', [])
                if not all_course_assessments:
                    print(f"  Empty assessments list for course {course.code}")
                    continue
                    
                total_assessments += len(all_course_assessments)
                
                # Count already scheduled assessments
                already_scheduled = sum(1 for a in all_course_assessments if a.get('scheduled'))
                scheduled_assessments += already_scheduled
                
                filtered_assessments = {
                    'code': assessments['code'],
                    'assessments': [a for a in all_course_assessments if not a.get('scheduled')]
                }
                
                print(f"  Course {course.code}: Found {len(all_course_assessments)} assessments, {len(filtered_assessments['assessments'])} unscheduled")
                
                if filtered_assessments['assessments']:
                    course_assessment_list.append(filtered_assessments)
            except Exception as e:
                print(f"Error processing course {course.code if course else 'unknown'}: {str(e)}")
                continue
                
        print(f"Summary: Found {total_assessments} total assessments, {scheduled_assessments} already scheduled")
        print(f"Found {len(course_assessment_list)} courses with unscheduled assessments")
        
        return course_assessment_list

    def compile_class_matrix(self) -> List[List[int]]:
        """Compile the course overlap matrix."""
        semester = get_active_semester()
        if not semester:
            print("No active semester found")
            return []
            
        course_list: List[str] = []
        for course in semester.courses:
            if course is not None:
                course_list.append(course.code)
            else:
                print("Warning: Found None course in semester courses list, skipping")
        
        if not course_list:
            print("No valid courses found in semester")
            return []
            
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
                
            if not matrix or len(matrix) == 0:
                print("Empty course matrix, cannot proceed with scheduling")
                return None
                
            if not phi_matrix or len(phi_matrix) == 0:
                print("Empty phi matrix, cannot proceed with scheduling")
                return None

            # Check that matrix dimensions match the number of courses
            if len(matrix) != len(courses):
                print(f"Matrix dimension mismatch: {len(matrix)} rows but {len(courses)} courses")
                print("This may indicate an issue with the course overlap data")
                # Continue anyway as the solver might still work with partial data
                
            total_assessments = sum(len(course['assessments']) for course in courses)
            if total_assessments == 0:
                print("No assessments to schedule")
                return None
                
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
                
            # Add a fallback for the case when stage2 raises an exception
            try:
                schedule, Y_star, probability = solve_stage2(
                    courses, matrix, phi_matrix, U_star, k, d, M
                )
            except Exception as stage2_error:
                print(f"Error in Stage 2: {str(stage2_error)}")
                print("The solver encountered an error while trying to schedule assessments.")
                print("Try increasing the max assessments per day or relaxing other constraints.")
                return None
            
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
            if not courses:
                print("No courses with unscheduled assessments found")
                return None
                
            matrix = self.compile_class_matrix()
            if not matrix:
                print("Failed to generate course matrix")
                return None
                
            try:
                phi_matrix = get_phi_matrix(matrix)
            except Exception as e:
                print(f"Error generating phi matrix: {str(e)}")
                print("This usually means there's an issue with the course overlap data")
                return None
                
            k = get_semester_duration(semester.id)
            if k <= 0:
                print(f"Invalid semester duration: {k}")
                return None
                
            d = semester.max_assessments
            if d <= 0:
                print(f"Invalid max assessments per day: {d}")
                return None
                
            M = semester.constraint_value
            if M <= 0:
                print(f"Invalid constraint value: {M}")
                return None
            
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