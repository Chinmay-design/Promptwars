from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, List
from ..models.schemas import AuthResponse, User
from ..services.auth import AuthService, get_current_user, UNIVERSITY_FACULTY_DIRECTORY

router = APIRouter(prefix="/auth", tags=["Authentication & SSO"])

@router.post("/login", response_model=AuthResponse)
async def login_with_sso(payload: Dict[str, str] = Body(...)):
    """
    University Single Sign-On (SSO) login endpoint.
    Accepts university email and issues a secure JWT token.
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="University email is required.")
    return AuthService.sso_login(email)

@router.get("/me", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated faculty/researcher profile.
    """
    return current_user

@router.get("/faculty-directory", response_model=List[Dict])
async def get_faculty_directory():
    """
    Returns list of faculty available for one-click SSO simulation.
    """
    return list(UNIVERSITY_FACULTY_DIRECTORY.values())
