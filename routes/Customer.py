import io
import pandas as pd
import matplotlib.pyplot as plt
import re
import pdfplumber
from fastapi import APIRouter,File,UploadFile
from models.Customer import customer,user,pieChart
from config.db import conn
from schemas.customer import serializeDict, serializeList
from fastapi.responses import FileResponse

customerRouter=APIRouter()

#Get Customer
@customerRouter.get('/')
async def findAllCustomers():
    return serializeList(conn.local.customer.find())

#Post Customer
@customerRouter.post('/')
async def SaveCustomer(cust:customer):
    conn.local.customer.insert_one(dict(cust))
    return serializeList(conn.local.customer.find())

#Post PDF
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
                    if(data[i].find('???')):
                        purchase+=data[i]
                    else:
                        if(counter==1):
                            amount=data[i]
                            counter=0
                        else:
                            points=data[i]
                            counter+=1
                conn.local.customer.find_one_and_update({"customerAccNumber":customerNumber},{"$push":{"customerCreditPurchase":{"date":date,"activity":purchase,"rewards_points":points,"amount_spent":amount}}},{"upsert":True})
        return customerNumber
    else:
        return customerNumber

            
    #return serializeList(conn.local.customer.find({"customerAccNumber":customerNumber}))

#Get Python Data Visuals
@customerRouter.get('/getVisual')
async def SaveCustomerDatas(cust:str):

    df=pd.DataFrame(list(conn.local.customer.find({"customerAccNumber": cust})))
    t=df["customerCreditPurchase"][0]
    dfmain=pd.DataFrame(list(t))
    text=dfmain["activity"]
    text=text.apply(lambda x : x.lower())

    labels={"electricity":"Household","gas":"Household","sewer":"Household","water":"Household"
            ,"trash":"Household","airtel":"Recharge","jio":"Recharge","bsnl":"Recharge",
            "netflix":"Streaming services","youtube":"Streaming services","hulu":"Streaming services",
            "disney+":"Streaming services","icici":"bank","indian bank":"bank","cub":"bank"
            ,"swiggy":"foods","zomato":"foods","pizzahut":"foods","uber eats":"foods","redbus":"travel"
            ,"airlines":"travel","makemytrip":"travel","oyo":"travel","d-mart":"grocery","bigbazaar":"grocery"
            ,"reliancefresh":"grocery","insurance":"insurance"}

    labs=[]
    for item in text:
        for types in list(labels.keys()):
            counter=0
            if(types in item):
                labs.append(labels[types])
                counter=1
                break
        if(counter==0):
            labs.append("miscellaneous")    

    dfmain["labels"]=pd.DataFrame(labs)
    text1=dfmain["amount_spent"]
    dfmain["spent"]=text1.apply(lambda x : float(x.strip("???")))

    label=dfmain["labels"].unique()
    counts=dfmain.groupby("labels").size()
    sums=dfmain.groupby("labels").sum()
    
    plt.figure(figsize=(16, 10))
    plt.bar(sums.index,sums["spent"])
    plt.savefig('img.png')
    file_path='img.png'
    return FileResponse(path=file_path, filename=file_path, media_type="image/png")

#Get All Users Graphs Python Data Visuals
@customerRouter.get('/getAllVisual')
async def SaveCustomerDatas():

    df=pd.DataFrame(list(conn.local.customer.find()))
    t=df["customerCreditPurchase"][0]
    listofAllCustomer=[]

    for i in range(0,len(df["customerCreditPurchase"])):
        listofAllCustomer.extend(df["customerCreditPurchase"][i])
    
    dfmain=pd.DataFrame(list(listofAllCustomer))
    text=dfmain["activity"]
    text=text.apply(lambda x : x.lower())

    labels={"electricity":"Household","gas":"Household","sewer":"Household","water":"Household"
            ,"trash":"Household","airtel":"Recharge","jio":"Recharge","bsnl":"Recharge",
            "netflix":"Streaming services","youtube":"Streaming services","hulu":"Streaming services",
            "disney+":"Streaming services","icici":"bank","indian bank":"bank","cub":"bank"
            ,"swiggy":"foods","zomato":"foods","pizzahut":"foods","uber eats":"foods","redbus":"travel"
            ,"airlines":"travel","makemytrip":"travel","oyo":"travel","d-mart":"grocery","bigbazaar":"grocery"
            ,"reliancefresh":"grocery","insurance":"insurance"}

    labs=[]
    for item in text:
        for types in list(labels.keys()):
            counter=0
            if(types in item):
                labs.append(labels[types])
                counter=1
                break
        if(counter==0):
            labs.append("miscellaneous")    

    dfmain["labels"]=pd.DataFrame(labs)
    text1=dfmain["amount_spent"]
    dfmain["spent"]=text1.apply(lambda x : float(x.strip("???")))

    label=dfmain["labels"].unique()
    counts=dfmain.groupby("labels").size()
    sums=dfmain.groupby("labels").sum()

    plt.figure(figsize=(16, 10))
    plt.bar(sums.index,sums["spent"])
    plt.savefig('img.png')
    
    file_path='img.png'
    return FileResponse(path=file_path, filename=file_path, media_type="image/png")

#Get User Pie Chart
@customerRouter.get("/user")
async def GetUser(cust:str):
    user_val=conn.local.customer.find_one({"customerAccNumber":cust})
    return serializeDict(user_val)

#Get All Users Graphs Python Data Visuals
@customerRouter.get('/getAllVisualPie')
async def SaveCustomerDatas():

    df=pd.DataFrame(list(conn.local.customer.find()))
    t=df["customerCreditPurchase"][0]
    listofAllCustomer=[]

    for i in range(0,len(df["customerCreditPurchase"])):
        listofAllCustomer.extend(df["customerCreditPurchase"][i])
    
    dfmain=pd.DataFrame(list(listofAllCustomer))
    text=dfmain["activity"]
    text=text.apply(lambda x : x.lower())

    labels={"electricity":"Household","gas":"Household","sewer":"Household","water":"Household"
            ,"trash":"Household","airtel":"Recharge","jio":"Recharge","bsnl":"Recharge",
            "netflix":"Streaming services","youtube":"Streaming services","hulu":"Streaming services",
            "disney+":"Streaming services","icici":"bank","indian bank":"bank","cub":"bank"
            ,"swiggy":"foods","zomato":"foods","pizzahut":"foods","uber eats":"foods","redbus":"travel"
            ,"airlines":"travel","makemytrip":"travel","oyo":"travel","d-mart":"grocery","bigbazaar":"grocery"
            ,"reliancefresh":"grocery","insurance":"insurance"}

    labs=[]
    for item in text:
        for types in list(labels.keys()):
            counter=0
            if(types in item):
                labs.append(labels[types])
                counter=1
                break
        if(counter==0):
            labs.append("miscellaneous")    

    dfmain["labels"]=pd.DataFrame(labs)
    text1=dfmain["amount_spent"]
    dfmain["spent"]=text1.apply(lambda x : float(x.strip("???")))

    label=dfmain["labels"].unique()
    counts=dfmain.groupby("labels").size()
    sums=dfmain.groupby("labels").sum()
    spent=list(sums["spent"])
    indexspent=list(sums.index)
    alluser=pieChart(label=indexspent,value=spent)
    return alluser