from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

# 사용자 기본 모델
class UserBase(BaseModel):
    NAME: str
    USER_EMAIL: EmailStr
    
    @field_validator('NAME')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('이름은 비어있을 수 없습니다')
        return v.strip()
    
    @field_validator('USER_EMAIL')
    @classmethod
    def email_must_not_be_empty(cls,v):
        if not v or len(v.strip())==0:
            raise ValueError('이메일은 비어있을 수 없습니다')
        return v.strip()

# 사용자 생성 모델 (요청)
class UserCreate(UserBase):
    PASSWORD: str
    
    @field_validator('PASSWORD')
    @classmethod
    def password_must_be_strong(cls, v):
        min_length = 8
        if len(v) < min_length:
            raise ValueError(f'비밀번호는 최소 {min_length}자 이상이어야 합니다')
        # 추가적인 비밀번호 정책 검증 로직 가능
        return v

# 사용자 응답 모델
class UserResponse(UserBase):
    USER_ID: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

# 토큰 응답 모델
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    team: Optional[dict] = None

# 토큰 데이터 모델
class TokenData(BaseModel):
    email: Optional[str] = None

class CheckNum(BaseModel):
    NAME: str
    ACCOUNT_NUM: str
    BOOL: bool
