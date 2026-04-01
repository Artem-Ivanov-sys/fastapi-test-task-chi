from typing import List, Annotated

from fastapi import HTTPException
from fastapi import Depends

from app.models.models import User
from app.core.auth import get_current_user

def require_role(required_roles: List[str]):
    def role_checker(curren_user: Annotated[User, Depends(get_current_user)]):
        if curren_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="forbidden")
        return curren_user
    return role_checker