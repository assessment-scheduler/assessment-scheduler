from ..database import db
from ..models import CourseTimetable

def create_timetable_entry(course_code, day_of_week, time_slot):
    """
    Create a new timetable entry for a course.
    
    Args:
        course_code (str): Course code
        day_of_week (int): Day of the week (1=Monday, 2=Tuesday, etc.)
        time_slot (str): Time slot (e.g. "09:00")
        
    Returns:
        CourseTimetable: The created timetable entry
    """
    entry = CourseTimetable(course_code, day_of_week, time_slot)
    
    db.session.add(entry)
    db.session.commit()
    
    return entry

def get_timetable_entries_by_course(course_code):
    """
    Get all timetable entries for a specific course.
    
    Args:
        course_code (str): Course code
        
    Returns:
        list: List of timetable entries
    """
    return CourseTimetable.query.filter_by(course_code=course_code).all()

def get_timetable_entries():
    """
    Get all timetable entries.
    
    Returns:
        list: List of all timetable entries
    """
    return CourseTimetable.query.all()

def get_day_mapping():
    """
    Get a mapping of day names to day numbers.
    
    Returns:
        dict: Dictionary mapping day names to numbers
    """
    return {
        'Monday': 1,
        'Mon': 1,
        'Tuesday': 2,
        'Tue': 2,
        'Wednesday': 3,
        'Wed': 3,
        'Thursday': 4,
        'Thu': 4,
        'Friday': 5,
        'Fri': 5
    }

def convert_to_timetable_format(entries, course_codes=None):
    """
    Convert timetable entries to the format needed for kris.py.
    
    Args:
        entries (list): List of CourseTimetable objects
        course_codes (list, optional): List of course codes in the order used by the solver
        
    Returns:
        dict: Dictionary mapping (course_idx, day_of_week) to True
    """
    timetable = {}
    
    # Create debug dictionary to print before returning
    debug_mapping = {}
    
    if course_codes:
        # Use the same course ordering as the solver
        code_to_idx = {code: idx for idx, code in enumerate(course_codes)}
        print(f"DEBUG: Using solver's course ordering with {len(course_codes)} courses")
    else:
        # Otherwise use alphabetical ordering
        unique_codes = sorted(set(entry.course_code for entry in entries))
        code_to_idx = {code: idx for idx, code in enumerate(unique_codes)}
        print(f"DEBUG: Using alphabetical ordering with {len(unique_codes)} courses")
    
    # Print the mapping for debugging
    print("DEBUG: Course code to index mapping:")
    for code, idx in sorted(code_to_idx.items()):
        print(f"DEBUG:   {code} -> {idx}")
    
    # Process each entry
    for entry in entries:
        if entry.course_code in code_to_idx:  # Make sure the course is in our mapping
            course_idx = code_to_idx[entry.course_code]
            day_of_week = entry.day_of_week
            timetable[(course_idx, day_of_week)] = True
            
            # Add to debug mapping
            if entry.course_code not in debug_mapping:
                debug_mapping[entry.course_code] = []
            debug_mapping[entry.course_code].append(day_of_week)
    
    # Print debug mapping
    print("DEBUG: Final timetable mapping:")
    for code, days in sorted(debug_mapping.items()):
        print(f"DEBUG:   {code} lectures on days: {sorted(days)}")
    
    return timetable, code_to_idx 