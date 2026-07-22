from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class ParticipantCreate(BaseModel):

    name: str = Field(..., min_length=1, max_length=100, description="Ім'я учасника")
    email: EmailStr = Field(..., description="Email учасника (унікальний)")
    event: str = Field(..., min_length=1, max_length=200, description="Назва заходу")
    age: int = Field(..., ge=12, le=120, description="Вік учасника (12-120)")

    @field_validator("name")
    @classmethod
    def name_must_not_contain_digits(cls, v: str) -> str:
        if any(char.isdigit() for char in v):
            raise ValueError("Ім'я не повинно містити цифр")
        return v.strip()

    @field_validator("event")
    @classmethod
    def event_must_not_be_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Назва заходу не може бути порожньою")
        return stripped


class ParticipantOut(BaseModel):

    id: int
    name: str
    email: str
    event: str
    age: int

    model_config = ConfigDict(from_attributes=True)