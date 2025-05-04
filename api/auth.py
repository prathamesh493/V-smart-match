from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from typing import Optional, Dict, Any
from pydantic import BaseModel
from services.firebase import get_db
from datetime import datetime

class UserData(BaseModel):
    """Schema for user authentication data"""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    candidate_id: Optional[str] = None

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class FirebaseAuth(HTTPBearer):
    """Firebase authentication handler for FastAPI"""
    
    def __init__(self, auto_error: bool = True):
        super(FirebaseAuth, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> UserData:
        """Extract and verify the Firebase ID token from the request"""
        credentials: HTTPAuthorizationCredentials = await super(FirebaseAuth, self).__call__(request)
        
        if not credentials or not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = credentials.credentials
        try:
            # Verify the Firebase token
            decoded_token = auth.verify_id_token(token)
            
            # Extract user information
            user_id = decoded_token.get("uid")
            email = decoded_token.get("email")
            name = decoded_token.get("name")
            
            if not user_id:
                raise AuthenticationError("Invalid token: missing user ID")
            
            # Check if user already exists in db and get candidate_id if possible
            candidate_id = await get_candidate_id_for_user(user_id)
                
            return UserData(user_id=user_id, email=email, name=name, candidate_id=candidate_id)
            
        except auth.InvalidIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except auth.ExpiredIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired authentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except auth.RevokedIdTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Revoked authentication token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except auth.CertificateFetchError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch certificates. Check Firebase connection.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )

class OptionalFirebaseAuth(HTTPBearer):
    """Optional Firebase authentication handler for FastAPI"""
    
    def __init__(self):
        super(OptionalFirebaseAuth, self).__init__(auto_error=False)
    
    async def __call__(self, request: Request) -> UserData:
        """Extract and verify the Firebase ID token from the request if present"""
        try:
            credentials: HTTPAuthorizationCredentials = await super(OptionalFirebaseAuth, self).__call__(request)
            
            if not credentials or not credentials.scheme == "Bearer":
                # Use a placeholder user ID for requests without authentication
                return UserData(user_id="anonymous")
                
            token = credentials.credentials
            
            try:
                # Verify the Firebase token
                decoded_token = auth.verify_id_token(token)
                
                # Extract user information
                user_id = decoded_token.get("uid")
                email = decoded_token.get("email")
                name = decoded_token.get("name")
                
                if not user_id:
                    return UserData(user_id="anonymous")
                
                # Check if user already exists in db and get candidate_id if possible
                candidate_id = await get_candidate_id_for_user(user_id)
                    
                return UserData(user_id=user_id, email=email, name=name, candidate_id=candidate_id)
                
            except Exception as e:
                # Fall back to anonymous user on any error
                print(f"Authentication error (optional auth): {str(e)}")
                return UserData(user_id="anonymous")
                
        except Exception as e:
            # Fall back to anonymous user on any error
            print(f"Authentication error (optional auth): {str(e)}")
            return UserData(user_id="anonymous")

async def get_candidate_id_for_user(user_id: str) -> Optional[str]:
    """
    Retrieves the candidate ID for a user from the database.
    If user doesn't exist or doesn't have a candidate profile, creates one.
    """
    try:
        db = get_db()
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            candidate_id = user_data.get("candidate_profile_id")
            
            # If user exists but no candidate profile, create one
            if not candidate_id:
                # Create a candidate profile for this user
                candidate_ref = db.collection("candidates").document(user_id)
                candidate_doc = candidate_ref.get()
                
                if not candidate_doc.exists:
                    timestamp = datetime.now()
                    candidate_data = {
                        "user_id": user_id,
                        "created_at": timestamp,
                        "updated_at": timestamp
                    }
                    candidate_ref.set(candidate_data)
                
                # Update user with reference to candidate profile
                user_ref.update({
                    "candidate_profile_id": user_id,
                    "has_candidate_profile": True
                })
                
                return user_id
            
            return candidate_id
        else:
            # Create new user and candidate profile
            timestamp = datetime.now()
            
            # Create candidate document
            candidate_ref = db.collection("candidates").document(user_id)
            candidate_data = {
                "user_id": user_id,
                "created_at": timestamp,
                "updated_at": timestamp
            }
            candidate_ref.set(candidate_data)
            
            # Create user document
            user_data = {
                "created_at": timestamp,
                "candidate_profile_id": user_id,
                "has_candidate_profile": True,
                "email": "",  # We don't have email since we just created this
                "display_name": ""
            }
            user_ref.set(user_data)
            
            print(f"Created new user with ID: {user_id}")
            return user_id
    
    except Exception as e:
        print(f"Error in get_candidate_id_for_user: {str(e)}")
        return None

# Create dependency for authentication
firebase_auth = FirebaseAuth()
get_current_user = firebase_auth

# Create dependency for optional authentication
optional_firebase_auth = OptionalFirebaseAuth()
get_optional_user = optional_firebase_auth