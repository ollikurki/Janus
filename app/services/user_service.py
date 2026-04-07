# User Service
# Business logic for user management

from typing import Optional, Tuple
from app.models import User, Person
from app import db


class UserService:
    """Service for user-related business logic."""
    
    DEFAULT_PAGE_SIZE = 50
    
    @staticmethod
    def get_all_users(page: int = 1, per_page: int = None) -> Tuple[list, int]:
        """Get users with pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page (default 50)
        
        Returns:
            Tuple of (users list, total count)
        """
        if per_page is None:
            per_page = UserService.DEFAULT_PAGE_SIZE
        
        query = db.session.query(
            User.id, User.username, User.group, User.email
        ).order_by(User.id.asc())
        
        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return users, total
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get a user by username."""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get a user by email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def username_exists(username: str) -> bool:
        """Check if a username is already taken."""
        return User.query.filter_by(username=username).first() is not None
    
    @staticmethod
    def create_user(
        firstname: str,
        lastname: str,
        password: str,
        clearance: int
    ) -> tuple[User, str]:
        """Create a new user with associated Person record.
        
        Returns:
            tuple: (User object, error_message or empty string)
        """
        username = f"{lastname}.{firstname}"
        
        if UserService.username_exists(username):
            return None, "Username already in use."
        
        if clearance == 1:
            group = 'Teacher'
        elif clearance == 2:
            group = 'Student'
        else:
            group = 'Admin'
        
        user = User(
            username=username,
            email=f"{username}@janus.local",
            clearance=clearance,
            group=group
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()
        
        person = Person(
            first_name=firstname,
            last_name=lastname,
            user_id=user.id
        )
        db.session.add(person)
        db.session.commit()
        
        return user, ""
    
    @staticmethod
    def delete_user(username: str) -> bool:
        """Delete a user by username.
        
        Returns:
            bool: True if user was deleted, False if not found
        """
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def search_users(search_term: str) -> list:
        """Search users by username."""
        return db.session.query(
            User.id, User.username, User.group, User.email
        ).filter(
            User.username == search_term
        ).all()
