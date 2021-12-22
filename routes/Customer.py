import re
import pdfplumber
from fastapi import APIRouter,File,UploadFile
from models.Customer import customer
from config.db import conn
from schemas.customer import serializeList

customerRouter=APIRouter()

@customerRouter.get('/')
async def findAllCustomers():
    return serializeList(conn.local.customer.find())

@customerRouter.post('/')
async def SaveCustomer(cust:customer):
    conn.local.customer.insert_one(dict(cust))
    return serializeList(conn.local.customer.find())

@customerRouter.post('/pdf')
async def SaveCustomerDatas(file:UploadFile = File(...)):

    with pdfplumber.open(file.file) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    customer_re = re.compile(r'Customer Number')

    for line in text.split('\n'):
        if customer_re.match(line):
            customerdata=line.split()
    customerNumber=customerdata[2]
    customerName=customerdata[3]+" "+customerdata[4]

    payment_re = re.compile(r'[A-Z].* Payment due on')

    for line in text.split('\n'):
        if payment_re.match(line):
            data=line.split()
            payment=data[6]+" "+data[7]+" "+data[8]
    

    allCustomers=serializeList(conn.local.customer.find())
    
    count=0

    for item in allCustomers:
        if(item["customerAccNumber"]==customerNumber):
            count+=1
    
    obj=customer(customerName=customerName,customerAccNumber=customerNumber,customerCreditPurchase=[],customerPaymentDue=[])

    if(count==0):
        conn.local.customer.insert_one(dict(obj))
    
    counter1=0

    Paymentcheck=serializeList(conn.local.customer.find({"customerAccNumber":customerNumber}))


    for item in Paymentcheck:
        if(payment in item["customerPaymentDue"]):
            counter1+=1
        else:
            counter1=0
    if(counter1==0):
        conn.local.customer.find_one_and_update({"customerAccNumber":customerNumber},{"$push":{"customerPaymentDue":payment}},{"upsert":True})
        credits_re=re.compile(r'^\d{1,2} [A-Z].*')
        points=""
        amount=""
        date="" 

        counter=0
        
        for line in text.split('\n'):
            if credits_re.match(line):
                data=line.split()
                purchase=""
                date=data[0]+" "+data[1]+" "+data[2]+" "+data[3]
                for i in range(4,len(data)):
                    if(data[i].find('$')):
                        purchase+=data[i]
                    else:
                        if(counter==1):
                            amount=data[i]
                            counter=0
                        else:
                            points=data[i]
                            counter+=1
                conn.local.customer.find_one_and_update({"customerAccNumber":customerNumber},{"$push":{"customerCreditPurchase":{"date":date,"activity":purchase,"rewards_points":points,"amount_spent":amount}}},{"upsert":True})
        return "Hi "+ customerName+"!! Your Last Payment Due Statement on "+payment+" of Account number "+customerNumber+ " is Added to the Database"
    else:
        return "Hi "+ customerName+"!! Your Last Payment Due Statement on "+payment+" of Account number "+customerNumber+ " is Already Added on the Database"

            
    #return serializeList(conn.local.customer.find({"customerAccNumber":customerNumber}))
