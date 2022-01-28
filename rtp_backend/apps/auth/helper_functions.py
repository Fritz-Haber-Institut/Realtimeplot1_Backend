"""
Contains functions that make the user model more accessible to other modules.
"""

from .models import User, UserTypeEnum


def is_admin(user: User) -> bool:
    """Returns True if the user is an admin. Otherwise False.
    If the user is None, the function returns False.

    Args:
        user (User): The user to check.

    Returns:
        bool: True if admin. Otherwise and if None False.
    """
    if user is None:
        return False
    if user.user_type is UserTypeEnum.admin:
        return True
    return False


def is_last_admin() -> bool:
    return User.query.filter_by(user_type=UserTypeEnum.admin).count() <= 1
