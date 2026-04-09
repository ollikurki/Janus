# Attendance Service
# Business logic for attendance management

from typing import Optional, Dict, List
from datetime import date, datetime, timedelta
from app.models import Student, Attendance, Groups, ATTENDANCE_STATUSES
from app import db


class AttendanceService:
    """Service for attendance-related business logic."""
    
    @staticmethod
    def get_today_attendance_count() -> int:
        """Get count of attendance records for today."""
        today = date.today()
        return Attendance.query.filter(
            Attendance.attendance == today
        ).count()
    
    @staticmethod
    def get_attendance_by_date(target_date: date) -> list:
        """Get all attendance records for a specific date."""
        return Attendance.query.filter(
            Attendance.attendance == target_date
        ).all()
    
    @staticmethod
    def get_attendance_by_student(student_id: int) -> list:
        """Get all attendance records for a specific student."""
        return Attendance.query.filter_by(student_id=student_id).all()
    
    @staticmethod
    def get_attendance_by_group(group_id: int) -> list:
        """Get all attendance records for a specific group."""
        return db.session.query(
            Attendance.id, Student.id, Student.full_name, Attendance.attendance,
            Attendance.status, Attendance.notes
        ).join(Attendance).filter(
            Student.id == Attendance.student_id,
            Student.group_id == group_id
        ).all()
    
    @staticmethod
    def log_attendance(
        student_ids: list[int],
        attendance_date: Optional[date] = None,
        status: str = 'present',
        notes: Optional[str] = None
    ) -> tuple[int, int]:
        """Log attendance for multiple students.
        
        Args:
            student_ids: List of student IDs to mark
            attendance_date: Date for attendance (defaults to today)
            status: Attendance status ('present', 'absent', 'excused', 'late')
            notes: Optional notes for the attendance record
        
        Returns:
            tuple: (number_created, number_skipped)
        """
        if status not in ATTENDANCE_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {ATTENDANCE_STATUSES}")
        
        if attendance_date is None:
            attendance_date = date.today()
        
        created = 0
        skipped = 0
        
        for student_id in student_ids:
            existing = AttendanceService._record_exists(student_id, attendance_date)
            if existing:
                # Update existing record with new status/notes
                existing.status = status
                if notes is not None:
                    existing.notes = notes
                skipped += 1
                continue
            
            record = Attendance(
                student_id=student_id,
                attendance=attendance_date,
                status=status,
                notes=notes
            )
            db.session.add(record)
            created += 1
        
        db.session.commit()
        return created, skipped
    
    @staticmethod
    def log_bulk_attendance(
        records: list[dict],
        attendance_date: Optional[date] = None
    ) -> tuple[int, int, int]:
        """Log attendance for multiple students with individual statuses.
        
        Args:
            records: List of dicts with keys: student_id, status, notes (optional)
            attendance_date: Date for attendance (defaults to today)
        
        Returns:
            tuple: (number_created, number_updated, number_skipped)
        """
        if attendance_date is None:
            attendance_date = date.today()
        
        created = 0
        updated = 0
        skipped = 0
        
        for rec in records:
            student_id = rec['student_id']
            status = rec.get('status', 'present')
            notes = rec.get('notes')
            
            if status not in ATTENDANCE_STATUSES:
                skipped += 1
                continue
            
            existing = AttendanceService._record_exists(student_id, attendance_date)
            if existing:
                existing.status = status
                if notes is not None:
                    existing.notes = notes
                updated += 1
            else:
                record = Attendance(
                    student_id=student_id,
                    attendance=attendance_date,
                    status=status,
                    notes=notes
                )
                db.session.add(record)
                created += 1
        
        db.session.commit()
        return created, updated, skipped
    
    @staticmethod
    def _record_exists(student_id: int, attendance_date: date) -> Optional[Attendance]:
        """Check if attendance record already exists for student on date.
        
        Returns the existing record if found, None otherwise.
        """
        return Attendance.query.filter_by(
            student_id=student_id,
            attendance=attendance_date
        ).first()
    
    @staticmethod
    def search_by_name(student_name: str) -> list:
        """Search attendance records by student name."""
        return db.session.query(
            Attendance.id, Student.id, Student.full_name, Attendance.attendance,
            Attendance.status, Attendance.notes
        ).join(Attendance).filter(
            Student.id == Attendance.student_id,
            Student.full_name == student_name
        ).order_by(Attendance.id.desc()).all()
    
    @staticmethod
    def search_by_date_range(start_date: date, end_date: date) -> list:
        """Search attendance records within a date range."""
        return db.session.query(
            Attendance.id, Student.id, Student.full_name, Attendance.attendance,
            Attendance.status, Attendance.notes
        ).join(Attendance).filter(
            Student.id == Attendance.student_id,
            Attendance.attendance.between(start_date, end_date)
        ).order_by(Attendance.id.desc()).all()
    
    @staticmethod
    def get_group_statistics(group_id: int, days: int = 30) -> Dict:
        """Get attendance statistics for a group over a period.
        
        Args:
            group_id: The group ID to get stats for
            days: Number of days to look back (default 30)
        
        Returns:
            Dict with total_students, total_records, attendance_rate, status_breakdown
        """
        start_date = date.today() - timedelta(days=days)
        
        # Get total students in group
        total_students = Student.query.filter_by(group_id=group_id).count()
        
        # Get attendance records for this group in date range
        records = db.session.query(Attendance).join(Student).filter(
            Student.group_id == group_id,
            Attendance.attendance >= start_date
        ).all()
        
        total_records = len(records)
        
        # Calculate possible attendances (students * days)
        possible_attendances = total_students * days
        
        # Count by status
        status_counts = {'present': 0, 'absent': 0, 'excused': 0, 'late': 0}
        for r in records:
            if r.status in status_counts:
                status_counts[r.status] += 1
        
        attendance_rate = 0.0
        if possible_attendances > 0:
            attendance_rate = round((total_records / possible_attendances) * 100, 1)
        
        return {
            'group_id': group_id,
            'group_name': Groups.query.get(group_id).marking if Groups.query.get(group_id) else 'Unknown',
            'period_days': days,
            'total_students': total_students,
            'total_records': total_records,
            'possible_attendances': possible_attendances,
            'attendance_rate': attendance_rate,
            'status_breakdown': status_counts
        }
    
    @staticmethod
    def get_trend_data(group_id: Optional[int] = None, days: int = 30) -> List[Dict]:
        """Get attendance trends over time.
        
        Args:
            group_id: Filter by group (optional)
            days: Number of days to look back (default 30)
        
        Returns:
            List of dicts with date and count
        """
        start_date = date.today() - timedelta(days=days)
        
        query = db.session.query(
            Attendance.attendance,
            db.func.count(Attendance.id).label('count')
        ).filter(Attendance.attendance >= start_date)
        
        if group_id:
            query = query.join(Student).filter(Student.group_id == group_id)
        
        results = query.group_by(Attendance.attendance).order_by(Attendance.attendance).all()
        
        return [
            {'date': r.attendance.isoformat(), 'count': r.count}
            for r in results
        ]
    
    @staticmethod
    def get_all_groups_statistics(days: int = 30) -> List[Dict]:
        """Get attendance statistics for all groups.
        
        Args:
            days: Number of days to look back (default 30)
        
        Returns:
            List of group statistics dicts
        """
        groups = Groups.query.all()
        return [
            AttendanceService.get_group_statistics(g.id, days)
            for g in groups
        ]
