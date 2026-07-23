from fastapi import FastAPI
from dashboard import fetch_user_dashboard

app = FastAPI(title="User Dashboard Aggregator")


@app.get("/user-dashboard/{user_id}")
def user_dashboard(user_id: int):
    return fetch_user_dashboard(user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8006)