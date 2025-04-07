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

def get_course_row(course_code: str, target_codes: List[str] = None) -> List[int]:

    if target_codes:
        # If target_codes is provided, get values in that specific order
        result = []
        for target_code in target_codes:
            cell = get_cell(course_code, target_code)
            result.append(cell.student_count if cell else 0)
        return result
    else:
        # Original behavior - get all cells ordered by code2
        course_cells = CourseOverlap.query.filter_by(code1=course_code).order_by(CourseOverlap.code2).all()
        return [cell.student_count for cell in course_cells]

def fill_empty_cells(course_codes:List[str]):
    for code1 in course_codes:
        for code2 in course_codes:
            cell = get_cell(code1,code2)
            if cell is None:
                create_cell(code1,code2,0)

def get_course_matrix(course_codes: List[str], debug: bool = False) -> List[List[int]]:

    # Ensure all required cells exist in the database
    fill_empty_cells(course_codes)
    
    if debug:
        print("\nDEBUG: Building course matrix...")
        print(f"DEBUG: Input course codes: {course_codes}")
    
    matrix: List = []
    for i, code in enumerate(course_codes):
        # Get the row using the improved get_course_row function
        row = get_course_row(code, course_codes)
        matrix.append(row)
    
    if debug:
        # Verify the matrix dimensionality
        print(f"DEBUG: Final matrix dimensions: {len(matrix)}x{len(matrix[0]) if matrix else 0}")
        
        # Sample the matrix to provide some visibility
        if matrix and len(matrix) > 0 and len(matrix[0]) > 0:
            # Sample up to first 5 courses if available
            sample_size = min(5, len(course_codes))
            print("Sample matrix values (first {} courses):".format(sample_size))
            for i in range(min(sample_size, len(matrix))):
                row_values = []
                for j in range(min(sample_size, len(matrix[i]))):
                    row_values.append(f"{course_codes[i]}-{course_codes[j]}: {matrix[i][j]}")
                print(f"  {', '.join(row_values)}")
    
    return matrix

def verify_matrix_consistency(matrix: List[List[int]], course_codes: List[str], debug: bool = False) -> List[List[int]]:
    fixed_count = 0
    
    for i, code1 in enumerate(course_codes):
        for j, code2 in enumerate(course_codes):
            # Get the actual database value
            db_value = get_overlap_value(code1, code2)
            
            # If matrix value doesn't match database, correct it
            if matrix[i][j] != db_value:
                if debug:
                    print(f"DEBUG: Correcting {code1}->{code2} from {matrix[i][j]} to {db_value}")
                matrix[i][j] = db_value
                fixed_count += 1
    
    if debug and fixed_count > 0:
        print(f"DEBUG: Fixed {fixed_count} inconsistencies in the matrix")
    
    return matrix

def get_phi_matrix(matrix: List[List[int]]) -> List[List[int]]:
    return [[1 if cell > 0 else 0 for cell in row] for row in matrix]