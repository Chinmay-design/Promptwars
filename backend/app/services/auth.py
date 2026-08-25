import jwt
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.schemas import User, UserRole, AuthResponse
from ..config import settings

security = HTTPBearer(auto_error=False)

# Seeded University SSO Faculty Directory
UNIVERSITY_FACULTY_DIRECTORY: Dict[str, Dict] = {
    "elena.vance@university.edu": {
        "id": "usr_vance_01",
        "name": "Dr. Elena Vance",
        "email": "elena.vance@university.edu",
        "department": "Computer Science & AI",
        "role": UserRole.RESEARCHER,
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
    },
    "marcus.thorne@university.edu": {
        "id": "usr_thorne_02",
        "name": "Dr. Marcus Thorne",
        "email": "marcus.thorne@university.edu",
        "department": "Genomics & Bioinformatics",
        "role": UserRole.RESEARCHER,
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"
    },
    "sarah.lin@university.edu": {
        "id": "usr_lin_03",
        "name": "Prof. Sarah Lin",
        "email": "sarah.lin@university.edu",
        "department": "Earth & Climate Sciences",
        "role": UserRole.DEPARTMENT_CHAIR,
        "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
    },
    "david.chen@university.edu": {
        "id": "usr_chen_04",
        "name": "Dr. David Chen",
        "email": "david.chen@university.edu",
        "department": "Neuroscience & Cognitive Science",
        "role": UserRole.RESEARCHER,
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"
    },
    "amanda.ross@university.edu": {
        "id": "usr_ross_05",
        "name": "Dean Amanda Ross",
        "email": "amanda.ross@university.edu",
        "department": "Office of Academic Research",
        "role": UserRole.ADMIN,
        "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"
    }
}

class AuthService:
    @staticmethod
    def create_access_token(user: User) -> str:
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user.id,
            "email": user.email,
            "name": user.name,
            "department": user.department,
            "role": user.role.value,
            "exp": expires
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    @staticmethod
    def sso_login(email: str) -> AuthResponse:
        user_data = UNIVERSITY_FACULTY_DIRECTORY.get(email.lower())
        if not user_data:
            # Auto-provision new researcher from university domain
            user_id = f"usr_{int(time.time())}"
            user_data = {
                "id": user_id,
                "name": email.split("@")[0].replace(".", " ").title(),
                "email": email,
                "department": "Interdisciplinary Research",
                "role": UserRole.RESEARCHER,
                "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80"
            }
            UNIVERSITY_FACULTY_DIRECTORY[email.lower()] = user_data

        user = User(**user_data)
        token = AuthService.create_access_token(user)
        return AuthResponse(access_token=token, user=user)

    @staticmethod
    def decode_token(token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return User(
                id=payload["sub"],
                email=payload["email"],
                name=payload["name"],
                department=payload["department"],
                role=UserRole(payload["role"]),
                avatar_url=None
            )
        except Exception:
            return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    if not credentials:
        # Default mock guest user if no auth header passed for smooth local usage
        return User(
            id="usr_vance_01",
            name="Dr. Elena Vance (Demo SSO)",
            email="elena.vance@university.edu",
            department="Computer Science & AI",
            role=UserRole.RESEARCHER,
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
        )
    user = AuthService.decode_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired SSO authentication token"
        )
    return user
