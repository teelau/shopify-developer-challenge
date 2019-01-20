from flask import Flask, request
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Numeric
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

app = Flask(__name__)
    
db_uri = 'mysql+pymysql://testusr:testpass@mysql:3306/shopdb'
engine = sqlalchemy.create_engine(db_uri)
engine.connect()

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id=Column(Integer, primary_key=True)
    title=Column(String(32))
    price=Column(Numeric)
    inventory_count=Column(Integer)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'inventory_count': self.inventory_count
        }

@app.route('/')
def welcome():
    return 'Welcome to Tea Shop'

@app.route('/products')
def products():
    product_id = request.args.get('id')

    if product_id is not None:
        product_result = session.query(Product).filter(Product.id == product_id)
        return json.dumps([p.serialize() for p in product_result])

    available = request.args.get('available')

    if available == 'true':
        logging.info("AVAILABLE")
        available_results = session.query(Product).filter(Product.inventory_count != 0)
        return json.dumps([p.serialize() for p in available_results])
    else:
        logging.info("HERE NOT AVAILABLE")
        results = session.query(Product).all() # query all product rows from products table
        return json.dumps([p.serialize() for p in results])

    # result = engine.execute("SELECT * FROM products")
    # metadata = sqlalchemy.MetaData()
    # products = sqlalchemy.Table('products', metadata, autoload=True, autoload_with=engine)
    # t = Table('testtable', metadata)



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0')
