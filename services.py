import uvicorn
from fastapi import FastAPI
from multiprocessing import Process

# Service 1: User Identity (Port 8001)
app_id = FastAPI()
@app_id.get("/users/{uid}")
def get_user(uid: str):
    db = {
        "101": {"id": "101", "name": "Alice Dev"},
        "102": {"id": "102", "name": "Bob Architect"}
    }
    return db.get(uid, {"error": "User not found in Identity Service"})

# Service 2: Corporate Directory (Port 8002)
app_dir = FastAPI()
@app_dir.get("/directory/{uid}")
def get_dir(uid: str):
    db = {
        "101": {"email": "alice@tech.co", "dept": "Backend"},
        "102": {"email": "bob@arch.co", "dept": "Infrastructure"}
    }
    return db.get(uid, {"error": "User not found in Directory Service"})

def run_id(): uvicorn.run(app_id, host="0.0.0.0", port=8001)
def run_dir(): uvicorn.run(app_dir, host="0.0.0.0", port=8002)

if __name__ == "__main__":
    print("Microservices Starting: Identity (8001) & Directory (8002)")
    p1 = Process(target=run_id); p2 = Process(target=run_dir)
    p1.start(); p2.start()
    p1.join(); p2.join()