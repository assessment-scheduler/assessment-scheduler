from datetime import timedelta
from typing import List
from ..models.assessment import Assessment
from ..controllers import (
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
    get_semester_duration
)

def compile_course_data() -> List:
    course_assessment_list: list = []
    courses: list = get_all_courses()
    for course in courses:
        assessments: List[Assessment] = get_assessment_dictionary_by_course(course.code)
        course_assessment_list.append(assessments)
    return course_assessment_list

def compile_class_matrix() -> List[List[int]]:
    course_list: List[str] = get_all_course_codes()
    matrix: List[List[int]] = get_course_matrix(course_list)
    return matrix


def compute_schedule():
    semester = get_active_semester()
    
    if semester is None:
        print("No active semester found")
        return None
    
    courses: List = compile_course_data()
    matrix: List[List[int]] = compile_class_matrix()
    phi_matrix: List[List[int]] = get_phi_matrix(matrix)
    
    k: int = get_semester_duration(semester.id)
    d = semester.max_assessments
    M: int = semester.constraint_value

    U_star, _, _ = solve_stage1(courses, matrix, k, M)
    schedule,Y_star, probability = solve_stage2(courses,matrix,phi_matrix,U_star,k,d,M)
    print_schedule(schedule, U_star, d, probability)
    return schedule


def schedule_all_assessments(schedule):
    semester = get_active_semester()
    if not semester:
        print("Could not schedule assessments, no active semester")
        return 
    for row in schedule:
        code = row[3]
        name = row[4].split('-')[0]
        schedule_date = semester.start_date + timedelta(days=int(row[1]))
        schedule_assessment(semester, schedule_date,code,name)



