from typing import List, Optional
from ..database import db
from ..models.courseoverlap import CourseOverlap

def get_cell(code1:str, code2:str) -> Optional[CourseOverlap]:
    return CourseOverlap.query.filter_by(code1=code1, code2=code2).first()

def get_overlap_value(code1:str,code2:str) -> int:
    cell = get_cell(code1, code2)
    return cell.student_count if cell else 0

def get_all_cells()-> List[CourseOverlap]:
    return CourseOverlap.query.all()

def create_cell(code1:str, code2:str, student_count:int) -> bool:
    if get_cell(code1, code2):
        return False
    new_cell = CourseOverlap(code1, code2, student_count)
    db.session.add(new_cell)
    db.session.commit()
    return True

def get_course_row(course_code:str) -> List[CourseOverlap]:
    course_cells = CourseOverlap.query.filter_by(code1 = course_code).order_by(CourseOverlap.code2).all()
    return [cell.student_count for cell in course_cells]

def fill_empty_cells(course_codes:List[str]):
    for code1 in course_codes:
        for code2 in course_codes:
            cell = get_cell(code1,code2)
            if cell is None:
                create_cell(code1,code2,0)


def get_course_matrix(course_codes: List[str]) -> List[List[int]]:
    fill_empty_cells(course_codes)
    matrix: List = []
    for code in course_codes:
        row: List[CourseOverlap] = get_course_row(code)
        matrix.append(row)
    return matrix

def get_phi_matrix(matrix: List[List[int]]) -> List[List[int]]:
    return [[1 if cell > 0 else 0 for cell in row] for row in matrix]