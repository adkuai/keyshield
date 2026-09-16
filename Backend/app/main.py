from fastapi import FastAPI       # type: ignore

app = FastAPI(
    title = "KeyShield Dev Engine",
    description = "Foundational backend service managing application access metrics.",
    version = "0.1.0"
)

@app.get("/")
def read_root():
    return {"message" : "KeyShield API is running"}