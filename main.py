import datetime

from flask import Flask, request, abort
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import CheckConstraint


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tables.db"
db = SQLAlchemy(app)


class Courier(db.Model):
    __tablename__ = "couriers"

    courier_id = db.Column(db.Integer, primary_key=True, unique=True)
    courier_type = db.Column(db.String)
    regions = db.relationship("Courier_regions", backref="courier")
    working_hours = db.relationship("Courier_work_hours", backref="courier")

    rating = db.Column(db.Float)
    earnings = db.Column(db.Integer, default=0)

class Courier_regions(db.Model):
    __tablename__ = "courier_regions"

    c_region_id = db.Column(db.Integer, primary_key=True, unique=True)
    courier_id = db.Column(db.Integer, db.ForeignKey("couriers"))
    region = db.Column(db.Integer)

    def __init__(self, region, courier_id):
        assert type(region) == int
        self.courier_id = courier_id
        self.region = region


class Courier_work_hours(db.Model):
    __tablename__ = "courier_work_hours"

    wo_ho_id = db.Column(db.Integer, primary_key=True, unique=True)
    courier_id = db.Column(db.Integer, db.ForeignKey("couriers"))
    start_time = db.Column(db.Integer)
    end_time = db.Column(db.Integer)

    def __init__(self, hours, courier_id):
        start, end = hours.split('-')
        start_h, start_m = map(int, start.split(':'))
        end_h, end_m = map(int, end.split(':'))
        assert 0 <= start_h <= 23
        assert 0 <= end_h <= 23
        assert 0 <= start_m <= 59
        assert 0 <= end_m <= 59

        self.start_time = start_h * 60 + start_m
        self.end_time = end_h * 60 + end_m
        self.courier_id = courier_id


class Orders(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, unique=True)
    wieght = db.Column(db.Integer)
    region = db.Column(db.Integer)
    deli_hours = db.relationship("Deli_hours", backref="order")

    assigned_to = db.Column(db.Integer)
    assigned_when = db.Column(db.DateTime)

class Deli_hours(db.Model):
    __tablename__ = "deli_hours"

    deli_id = db.Column(db.Integer, primary_key=True, unique=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders"))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

@app.route("/couriers", methods=["POST"])
def post_couriers():
    if not request.is_json:
        abort (400, message="Data format not json")
    if "data" not in request.json.keys():
        abort (400, message="Data not found")

    result = {"couriers" : [] }
    failure = {"validation_error": {"couriers": [] }}

    right_types = set(["foot", "bike", "auto"])
    right_keys = set(["courier_id", "courier_type", "regions", "working_hours"])

    for courier in request.json["data"]:

        keys = set(courier.keys())
        if keys - right_keys or right_keys - keys:
            try:
                print ("key failed")
                failure["validation_error"]["couriers"].append(courier["courier_id"])
            except:
                return abort(400)

        if True:
            assert courier["courier_id"] > 0
            for hours in courier["working_hours"]:
                hours_to_commit = Courier_work_hours(hours=hours, courier_id=courier["courier_id"])
                db.session.add(hours_to_commit)
            for region in courier["regions"]:
                region_to_commit = Courier_regions(region=region, courier_id=courier["courier_id"])
                db.session.add(region_to_commit)
            if courier["courier_type"] not in right_types or Courier.query.filter_by(courier_id=courier["courier_id"]).all():
                failure["validation_error"]["couriers"].append(courier["courier_id"])
            else:
                courier_to_commit = Courier(courier_id=courier["courier_id"], courier_type=courier["courier_type"])
                db.session.add(courier_to_commit)
                result["couriers"].append(courier["courier_id"])
        else:
            failure["validation_error"]["couriers"].append(courier["courier_id"])

    if failure["validation_error"]["couriers"]:
        return (failure, 400)
    db.session.commit()
    return (result, 201)


@app.route("/couriers/<courier_id>", methods=["PATCH"])
def patch_couriers(courier_id):
    return {404: "not implemented"}


@app.route("/orders/assign", methods=["POST"])
def assign_orders():
    return {404: "not implemented"}


@app.route("/orders/complete", methods=["POST"])
def complete_orders():
    return {404: "not implemented"}


@app.route("/orders", methods=["POST"])
def post_orders():
    return {404: "not implemented"}


@app.route("/couriers/<courier_id>", methods=["GET"])
def get_courier(courier_id):
    return {404: "not implemented"}


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8080)