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

def jsonify(result):
    return json.dumps([p.serialize() for p in result])

# Routes

# Welcome page route
@app.route('/')
def welcome():
    return 'welcome to teashopify'

@app.route('/products', methods=['GET'])
def products():
    """
    
    """
    product_id = request.args.get('id')
    if product_id is not None:
        product_result = session.query(Product).filter(Product.id == product_id).first()
        if product_result is None:
            return 'Product id does not exist', 404
        return json.dumps(product_result.serialize())

    available = request.args.get('available')
    if available == 'true':
        available_results = session.query(Product).filter(Product.inventory_count != 0)
        return jsonify(available_results), 200
    else:
        results = session.query(Product) # query all product rows from products table
        return jsonify(results), 200

@app.route('/purchase', methods=['PUT'])
def purchase ():
    product_id = request.args.get('id')
    product_result = session.query(Product).filter(Product.id == product_id).first()
    # logging.info(Product)
    # return 1
    if product_result is None:
        return 'Product id does not exist', 404
    if product_result.serialize()['inventory_count'] <= 0:
        return 'Product is out of stock', 409
    session.query(Product).filter(Product.id == product_id).update({'inventory_count': Product.inventory_count - 1})
    session.commit()
    return 'Purchased 1 title: {} product_id: {}'.format( product_result.serialize()['title'], product_id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0')
