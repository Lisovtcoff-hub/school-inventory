from pydantic import BaseModel, Field


class ActivateOrganizationRequest(BaseModel):
    license_code: str = Field(min_length=3, max_length=50)

    organization_name: str = Field(min_length=2, max_length=255)

    admin_email: str = Field(min_length=3, max_length=255)
    admin_password: str = Field(min_length=6, max_length=128)
    admin_full_name: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    organization_id: int

    model_config = {
        "from_attributes": True
    }


class AuthOrganizationResponse(BaseModel):
    id: int
    public_id: str
    name: str

    model_config = {
        "from_attributes": True
    }


class ActivateOrganizationResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse
    organization: AuthOrganizationResponse


class MeResponse(BaseModel):
    user: AuthUserResponse
    organization: AuthOrganizationResponse