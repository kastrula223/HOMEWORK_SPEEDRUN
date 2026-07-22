from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Users API")

users = []


class UserRequest(BaseModel):
    name: str


def add_user(name: str) -> None:
    if name in users:
        raise HTTPException(status_code=400, detail=f"Користувач '{name}' вже існує.")
    users.append(name)


@app.post("/users")
def create_user(user: UserRequest):
    name = user.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Ім'я не може бути порожнім.")

    add_user(name)
    return {"message": f"Користувача '{name}' додано.", "users": users}


@app.get("/users")
def get_users():
    return {"users": users}


@app.delete("/users/{name}")
def delete_user(name: str):
    if name not in users:
        raise HTTPException(status_code=404, detail=f"Користувача '{name}' не знайдено.")

    users.remove(name)
    return {"message": f"Користувача '{name}' видалено.", "users": users}


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)