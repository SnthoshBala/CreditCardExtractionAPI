from fastapi import FastAPI
from routes.Customer import customerRouter
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
app.include_router(customerRouter)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)