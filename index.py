from fastapi import FastAPI
from routes.Customer import customerRouter

app=FastAPI()
app.include_router(customerRouter)