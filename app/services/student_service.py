# Student Service
# Business logic for student management

from typing import Optional, Tuple
from app.models import Student, Person, Groups
from app import db


class StudentService:
    """Service for student-related business logic."""
    
    DEFAULT_PAGE_SIZE = 50
    
    @staticmethod
    def get_all_students(page: int = 1, per_page: int = None) -> Tuple[list, int]:
        """Get students with pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page (default 50)
        
        Returns:
            Tuple of (students list, total count)
        """
        if per_page is None:
            per_page = StudentService.DEFAULT_PAGE_SIZE
        
        query = Student.query.order_by(Student.id.asc())
        total = query.count()
        students = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return students, total
    
    @staticmethod
    def get_student_by_id(student_id: int) -> Optional[Student]:
        """Get a student by ID."""
        return Student.query.get(student_id)
    
    @staticmethod
    def get_students_by_group(group_id: int) -> list:
        """Get all students in a specific group."""
        return Student.query.filter_by(group_id=group_id).all()
    
    @staticmethod
    def get_student_count() -> int:
        """Get total number of students."""
        return Student.query.count()
    
    @staticmethod
    def create_student(
        firstname: str,
        lastname: str,
        group_id: int
    ) -> Student:
        """Create a new student with associated Person record.
        
        Returns:
            Student: The created student object
        """
        full_name = f"{firstname} {lastname}"
        
        student = Student(
            group_id=group_id,
            full_name=full_name
        )
        db.session.add(student)
        db.session.flush()
        
        person = Person(
            first_name=firstname,
            last_name=lastname,
            student_id=student.id
        )
        db.session.add(person)
        db.session.commit()
        
        return student
    
    @staticmethod
    def get_groups() -> list:
        """Get all groups for form choices.
        
        Returns:
            list: List of (id, marking) tuples
        """
        groups = Groups.query.all()
        return [(g.id, g.marking) for g in groups]
