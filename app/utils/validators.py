import re

def validate_phone_number(phone: str) -> tuple[bool, str]:
    """
    Validate phone number: must be 10+ digits
    Returns: (is_valid, error_message)
    """
    # Remove common separators
    cleaned = phone.replace("-", "").replace(" ", "").replace("+", "")
    
    if not cleaned.isdigit():
        return False, "Phone number must contain only digits"
    
    if len(cleaned) < 10:
        return False, "Phone number must be at least 10 digits"
    
    return True, ""

def validate_credentials(username: str, password: str) -> str:
    """
    Validate login credentials
    Returns error message if invalid, empty string if valid
    """
    if not username or len(username) < 3:
        return "Username must be at least 3 characters"
    
    if not password or len(password) < 6:
        return "Password must be at least 6 characters"
    
    return ""

def validate_student_data(name: str, grade: str, phone: str, parent_contact: str) -> dict:
    """
    Validate student data
    Returns: {"valid": bool, "errors": [list of error messages]}
    """
    errors = []
    
    if not name or len(name.strip()) < 2:
        errors.append("Student name must be at least 2 characters")
    
    if not grade or len(grade.strip()) == 0:
        errors.append("Grade is required")
    
    # Validate parent contact
    is_valid_phone, error_msg = validate_phone_number(parent_contact)
    if not is_valid_phone:
        errors.append(f"Parent contact: {error_msg}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def validate_fee_data(amount: float, month: str) -> dict:
    """
    Validate fee data
    Returns: {"valid": bool, "errors": [list of error messages]}
    """
    errors = []
    
    if not amount or amount <= 0:
        errors.append("Amount must be greater than 0")
    
    if not month or len(month.strip()) == 0:
        errors.append("Month is required")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def validate_mark_data(subject: str, marks: float, total_marks: float) -> dict:
    """
    Validate mark data
    Returns: {"valid": bool, "errors": [list of error messages]}
    """
    errors = []
    
    if not subject or len(subject.strip()) == 0:
        errors.append("Subject is required")
    
    if marks < 0:
        errors.append("Marks cannot be negative")
    
    if total_marks <= 0:
        errors.append("Total marks must be greater than 0")
    
    if marks > total_marks:
        errors.append("Marks cannot exceed total marks")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
