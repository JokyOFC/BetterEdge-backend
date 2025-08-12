'''

Main project file

created in 12/08/2025 by Joky

'''

from fastapi import FastAPI

app = FastAPI(title="InvestApp", version="1.0")

@app.get("/")
def home():
    return {"status": "ok", "message": "API de investimento pronta!"}
