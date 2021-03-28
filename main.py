from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tables.db"
db = SQLAlchemy(app)

class Courier(db.Model):
    __tablename__ = "couriers"

    courier_id = db.Column(db.Integer, primary_key=True)
    courier_type = db.Column(db.String)
    regions = db.relationship("Courier_regions", backref="courier")
    working_hours = db.relationship("Courier_work_hours", backref="courier")


class Courier_regions(db.Model):
    __tablename__ = "courier_regions"

    c_region_id = db.Column(db.Integer, primary_key=True)
    courier_id = db.Column(db.Integer, db.ForeignKey("couriers"))
    region = db.Column(db.Integer)


class Courier_work_hours(db.Model):
    __tablename__ = "courier_work_hours"

    wo_ho_id = db.Column(db.Integer, primary_key=True)
    courier_id = db.Column(db.Integer, db.ForeignKey("couriers"))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)


class Orders(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    wieght = db.Column(db.Integer)
    region = db.Column(db.Integer)
    deli_hours = db.relationship("Deli_hours", backref="order")


class Deli_hours(db.Model):
    __tablename__ = "deli_hours"

    deli_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders"))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)


@app.route("/couriers", methods=["POST"])
def post_couriers():
    return None


@app.route("/couriers/<courier_id>", methods=["PATCH"])
def patch_couriers(courier_id):
    return courier_id


@app.route("/orders/assign", methods=["POST"])
def assign_orders():
    return None


@app.route("/orders/complete", methods=["POST"])
def complete_orders():
    return None


@app.route("/orders", methods=["POST"])
def post_orders():
    return None


@app.route("/couriers/<courier_id>", methods=["GET"])
def get_courier(courier_id):
    return courier_id

@app.route("/reset", methods=["GET"])
def reset_db():
    return 200, "db was deleted"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)