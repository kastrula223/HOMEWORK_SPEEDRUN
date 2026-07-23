from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator


class CalculateRequest(BaseModel):
    operation: Literal["factorial", "primes", "matrix_multiply", "array_stats"]

    n: Optional[int] = Field(None, description="Число для факторіалу (0-1000)")

    range_start: Optional[int] = Field(None, description="Початок діапазону пошуку простих")
    range_end: Optional[int] = Field(None, description="Кінець діапазону пошуку простих")

    matrix_size: Optional[int] = Field(None, description="Розмір матриці NxN (1-200)")

    array_size: Optional[int] = Field(None, description="Розмір масиву, якщо генерувати випадково")
    data: Optional[list[float]] = Field(None, description="Готовий масив чисел (альтернатива array_size)")

    @model_validator(mode="after")
    def check_required_fields(self):
        if self.operation == "factorial" and self.n is None:
            raise ValueError("Для operation='factorial' обов'язкове поле 'n'.")

        if self.operation == "primes" and (self.range_start is None or self.range_end is None):
            raise ValueError("Для operation='primes' обов'язкові поля 'range_start' і 'range_end'.")

        if self.operation == "matrix_multiply" and self.matrix_size is None:
            raise ValueError("Для operation='matrix_multiply' обов'язкове поле 'matrix_size'.")

        if self.operation == "array_stats" and self.array_size is None and self.data is None:
            raise ValueError("Для operation='array_stats' потрібне 'array_size' або готовий масив 'data'.")

        return self


class CalculateResponse(BaseModel):
    operation: str
    execution_time_seconds: float
    result: dict