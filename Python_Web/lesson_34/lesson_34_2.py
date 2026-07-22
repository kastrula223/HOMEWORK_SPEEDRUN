from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="To-Do List API")

tasks: dict[int, "Task"] = {}
next_id = 1


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Назва завдання")
    description: Optional[str] = Field(None, max_length=1000, description="Опис завдання")
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = False


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_data: TaskCreate):
    global next_id
    task = Task(id=next_id, **task_data.model_dump())
    tasks[next_id] = task
    next_id += 1
    return task


@app.get("/tasks", response_model=list[Task])
def get_all_tasks():
    return list(tasks.values())


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Завдання з id={task_id} не знайдено.")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskUpdate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Завдання з id={task_id} не знайдено.")

    updated_task = Task(id=task_id, **task_data.model_dump())
    tasks[task_id] = updated_task
    return updated_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Завдання з id={task_id} не знайдено.")
    del tasks[task_id]
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)