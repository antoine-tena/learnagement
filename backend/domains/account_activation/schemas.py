from pydantic import BaseModel, ConfigDict, Field

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 72  # bcrypt ignore les octets au-delà


class ActivationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: str = Field(min_length=1, max_length=100)


class ActivationLink(BaseModel):
    token: str
    expires_at: str


class ActivationConfirm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


class ActivationDone(BaseModel):
    is_activated: bool
