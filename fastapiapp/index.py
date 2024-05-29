from fastapi import Request, FastAPI, Form
import string, random
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
from typing import Annotated

import sqlalchemy

app = FastAPI()

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = "datalabs-hs:asia-southeast2:db-proxysql"  # e.g. 'project:region:instance'
    db_user = "root"  # e.g. 'my-db-user'
    db_pass = "P/X8d;YMqB}=]@e<"  # e.g. 'my-db-password'
    db_name = "storedb"  # e.g. 'my-database'

    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://root:P/X8d;YMqB}=]@e<@34.128.121.90/storedb",
        creator=getconn,
        # ...
    )
    return pool

pool=connect_with_connector()


@app.get("/v1/hello-world")
def read_root():
    return {"Hello": "World"}

@app.get("/v1/get-list-item")
async def get_list_item():
    with pool.connect() as connection:
        get_list_data=connection.execute(sqlalchemy.text("SELECT * FROM item_table")).fetchall()
        connection.commit()
        connection.close()
        items=[]
        for data in get_list_data:
            sku=data[0]
            name=data[1]
            desc=data[2]
            price=data[3]
            items.append({"sku":sku, "name":name, "desc":desc, "price":price})
        return items
    
@app.get("/v1/get-item")
async def get_item(sku: Annotated[str, Form()]):
    with pool.connect() as connection:
        get_data=connection.execute(sqlalchemy.text(f"SELECT * FROM item_table where sku='{sku}'")).fetchall()
        connection.commit()
        connection.close()
        if len(get_data) != 0 :
            items=[]
            for data in get_data:
                sku=data[0]
                name=data[1]
                desc=data[2]
                price=data[3]
                items.append({"sku":sku, "name":name, "desc":desc, "price":price})
                return items
        else:
            return {"message":"No data with sku "+sku}

@app.post("/v1/register-item")
async def register_item(request: Request):
    body =  await request.json()
    name = body["name"]
    desc = body["desc"]
    price = body["price"]
    sku = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    with pool.connect() as connection:
        insert_data=connection.execute(sqlalchemy.text("INSERT INTO item_table (sku, name, `desc`, price) VALUES (:sku, :name, :desc, :price)"), parameters={"sku":sku, "name":name, "desc":desc, "price":price})
        connection.commit()
        connection.close()
    return {"sku": sku,"name": name, "desc":desc, "price":price}

