from pydantic import BaseModel

from typing import List

class creditCardDetails(BaseModel):
    date:str
    activity:str
    rewards_points:str
    amount_spent:str

class customer(BaseModel):
    customerName:str
    customerAccNumber:str
    customerCreditPurchase:List[creditCardDetails]
    customerPaymentDue:list