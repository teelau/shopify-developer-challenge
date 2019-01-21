from flask import Flask, request
import sqlalchemy
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
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
    product_id = Column(Integer, primary_key=True)
    title = Column(String(32))
    price = Column(Numeric)
    inventory_count = Column(Integer)

    def serialize(self):
        return {
            'product_id': self.product_id,
            'title': self.title,
            'price': self.price,
            'inventory_count': self.inventory_count
        }


class ShoppingCart(Base):
    __tablename__ = 'shopping_carts'
    shopping_cart_id = Column(Integer, primary_key=True)


class ShoppingCartProducts(Base):
    __tablename__ = 'shopping_cart_products'
    id = Column(Integer, primary_key=True)
    shopping_cart_id = Column(Integer, ForeignKey('shopping_carts.shopping_cart_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))


def jsonify(result):
    """
    Helper function converts Product objects to JSON
    """
    return json.dumps([p.serialize() for p in result])


@app.route('/')
def welcome():
    """
    Welcome page route, serves as the landing page and friendly welcome to guests.
    """
    return 'welcome to teashopify'


@app.route('/products', methods=['GET'])
def products():
    """
    /products queries the shop database for available products.
    Allows the user to query products by id or by inventory count

    Parameters
    ----------
    Returns
    -------

    """
    product_id = request.args.get('product_id')
    product_query = session.query(Product)
    if product_id is not None:
        product_result = product_query.filter(Product.product_id == product_id).first()
        if product_result is None:
            return 'Product id does not exist', 404
        return json.dumps(product_result.serialize())

    available = request.args.get('available')
    if available == 'true':
        available_results = product_query.filter(Product.inventory_count != 0)
        return jsonify(available_results), 200
    else:
        results = product_query  # query all product rows from products table
        return jsonify(results), 200


@app.route('/purchase', methods=['PUT'])
def purchase():
    """
    """
    product_id = request.args.get('product_id')
    product_result = session.query(Product).filter(Product.product_id == product_id).first()
    if product_result is None:
        return 'Product id does not exist', 404
    if product_result.serialize()['inventory_count'] <= 0:
        return 'Product is out of stock', 409
    session.query(Product).filter(Product.id == product_id).update({'inventory_count': Product.inventory_count - 1})
    session.commit()
    return 'Purchased 1 title: {} product_id: {}'.format(product_result.serialize()['title'], product_id)


@app.route('/shopping_carts', methods=['POST', 'PUT', 'GET'])
def shopping_carts():
    """
    """
    if request.method == 'POST':
        shopping_cart = ShoppingCart()
        session.add(shopping_cart)
        session.commit()
        return json.dumps({'shopping_cart_id': shopping_cart.shopping_cart_id}), 201  # shopping cart created, with id returned

    elif request.method == 'PUT':
        add_product = request.args.get('product')
        product_result = session.query(Product).filter(Product.product_id == add_product).first()
        if product_result is None:
            return 'Product id does not exist', 404
        if product_result.serialize()['inventory_count'] <= 0:
            return 'Product is out of stock', 409

        add_cart = request.args.get('cart')
        cart_result = session.query(ShoppingCart).filter(ShoppingCart.shopping_cart_id == add_cart).first()
        if cart_result is None:
            return 'Cart id does not exist', 404

        cart_product_result = session.query(ShoppingCartProducts).filter(ShoppingCartProducts.product_id == add_product).filter(ShoppingCartProducts.shopping_cart_id == add_cart).first()
        if cart_product_result is not None:
            return 'Product already added to cart', 409

        shopping_cart_products = ShoppingCartProducts(product_id=add_product, shopping_cart_id=add_cart)
        session.add(shopping_cart_products)
        session.commit()
        return 'Product #{} added to cart #{}'.format(add_product, add_cart), 200


@app.route('/shopping_carts/total', methods=['GET'])
def shopping_cart_total_price():
    """
    """
    cart_id = request.args.get('cart')
    cart_result = session.query(ShoppingCart).filter(ShoppingCart.shopping_cart_id == cart_id).first()
    if cart_result is None:
        return 'Cart id does not exist', 404

    total = session.execute(
        ("SELECT SUM(products.price) AS 'total' FROM shopping_cart_products "
         "LEFT JOIN products "
         "ON products.product_id = shopping_cart_products.product_id "
         "WHERE shopping_cart_products.shopping_cart_id = :cart_id"),
        {"cart_id": cart_id}).first()['total']

    if total is None:
        total = 0

    return json.dumps({
        'total': total
    })


@app.route('/shopping_carts/purchase', methods=['PUT'])
def shopping_cart_purchase():
    """
    """
    cart_id = request.args.get('cart')
    cart_result = session.query(ShoppingCart).filter(ShoppingCart.shopping_cart_id == cart_id).first()
    if cart_result is None:
        return 'Cart id does not exist', 404

    out_of_stock = session.execute(
        ("SELECT COUNT(*) AS 'out' FROM shopping_cart_products "
         "LEFT JOIN products "
         "ON shopping_cart_products.product_id = products.product_id "
         "WHERE shopping_cart_products.shopping_cart_id = :cart_id "
         "AND products.inventory_count = 0"),
        {"cart_id": cart_id}).first()['out']

    if out_of_stock > 0:
        return 'Cannot complete purchase, a product ran out of stock', 400

    session.execute(
        ("UPDATE products "
         "INNER JOIN shopping_cart_products "
         "ON shopping_cart_products.product_id = products.product_id "
         "SET products.inventory_count = products.inventory_count -1 "
         "WHERE shopping_cart_products.shopping_cart_id = :cart_id "
         "AND products.inventory_count > 0"),
        {"cart_id": cart_id})

    session.execute(
        ("DELETE FROM shopping_cart_products "
         "WHERE shopping_cart_id = :cart_id "),
        {"cart_id": cart_id})
    session.commit()
    return 'Completed purchase for shopping cart!'


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0')
