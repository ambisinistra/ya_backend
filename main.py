import datetime
from dateutil import parser

from flask import Flask, request, abort
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


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
        assert region > 0
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


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, unique=True)
    weight = db.Column(db.Integer)
    region = db.Column(db.Integer)
    deli_hours = db.relationship("Deli_hours", backref="order")

    assigned_to = db.Column(db.Integer, default=0)
    assigned_when = db.Column(db.String)
    cour_type = db.Column(db.String)

    completed = db.Column(db.Integer, default=0)
    completed_when = db.Column(db.String)

class Deli_hours(db.Model):
    __tablename__ = "deli_hours"

    deli_id = db.Column(db.Integer, primary_key=True, unique=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders"))
    start_time = db.Column(db.Integer)
    end_time = db.Column(db.Integer)

    def __init__(self, hours, order_id):
        start, end = hours.split('-')
        start_h, start_m = map(int, start.split(':'))
        end_h, end_m = map(int, end.split(':'))
        assert 0 <= start_h <= 23
        assert 0 <= end_h <= 23
        assert 0 <= start_m <= 59
        assert 0 <= end_m <= 59

        self.start_time = start_h * 60 + start_m
        self.end_time = end_h * 60 + end_m
        self.order_id = order_id


@app.route("/couriers", methods=["POST"])
def post_couriers():
    if not request.is_json:
        abort (400, "Data format not json")
    if "data" not in request.json.keys():
        abort (400, "Data not found")

    result = {"couriers" : [] }
    failure = {"validation_error": {"couriers": [] }}

    right_types = set(["foot", "bike", "car"])
    right_keys = set(["courier_id", "courier_type", "regions", "working_hours"])

    for courier in request.json["data"]:

        keys = set(courier.keys())
        if keys - right_keys or right_keys - keys:
            try:
                failure["validation_error"]["couriers"].append(courier["courier_id"])
                break
            except:
                return abort(400)

        try:
            assert courier["courier_id"] > 0
            assert courier["working_hours"]
            assert courier["regions"]
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
        except:
            failure["validation_error"]["couriers"].append({"id" : courier["courier_id"]})

    if failure["validation_error"]["couriers"]:
        return (failure, 400)
    db.session.commit()
    return (result, 201)


@app.route("/orders", methods=["POST"])
def post_orders():
    if not request.is_json:
        return abort (400, "Data format not json")
    if "data" not in request.json.keys():
        return abort (400, "Data not found")

    result = {"orders" : [] }
    failure = {"validation_error": {"orders": [] }}

    right_keys = set(["order_id", "weight", "region", "delivery_hours"])

    for order in request.json["data"]:

        keys = set(order.keys())
        if keys - right_keys or right_keys - keys:
            try:
                failure["validation_error"]["orders"].append(order["order_id"])
                break
            except:
                return abort(400)

        try:
            assert order["order_id"] > 0
            assert order["region"] > 0
            assert order["delivery_hours"]
            weight = int(order["weight"] * 100)
            assert 1 <= weight <= 5000
            for hours in order["delivery_hours"]:
                hours_to_commit = Deli_hours(hours=hours, order_id=order["order_id"])
                db.session.add(hours_to_commit)
            if Order.query.filter_by(order_id=order["order_id"]).all():
                failure["validation_error"]["orders"].append(order["order_id"])
            else:
                order_to_commit = Order(order_id=order["order_id"], weight=order["weight"], region=order["region"])
                db.session.add(order_to_commit)
                result["orders"].append(order["order_id"])
        except:
            failure["validation_error"]["orders"].append({"id":order["order_id"]})

    if failure["validation_error"]["orders"]:
        return (failure, 400)
    db.session.commit()
    return (result, 201)


@app.route("/couriers/<courier_id>", methods=["PATCH"])
def patch_couriers(courier_id):
    if not request.is_json:
        return abort (400, "Data format not json")
    right_keys = set(["courier_type", "regions", "working_hours"])
    if set(request.json.keys()) - right_keys:
        return abort (400)

    couriers = Courier.query.filter_by(courier_id=request.json["courier_id"]).all()
    if not couriers:
        return ("Courier not found", 404)
    courier = couriers[0]
    result = {"courier_id": courier_id, "courier_type": 0, "working_hours": [], "regions": []}
    if True:
        wrong_orders = []
        if "regions" in request.json.keys():
            assert reqest.json["regions"]
            old_regions = Courier_regions.query.filter_by(courier_id=courier.courier_id)
            for old_region in old_regions:
                db.session.delete(old_region)
            for new_region in courier["regions"]:
                region_to_commit = Courier_regions(region=new_region, courier_id=courier["courier_id"])
                db.session.add(region_to_commit)
            wrong_orders.append(Order.query.filter_by(assigned_to=courier["courier_id"]).filter_by(completed=0).filter(not_(Order.region.in_(courier["regions"]))).all())

        if "courier_type" in request.json.keys():
            weights = {"foot": 1000, "bike": 1500, "car": 5000}
            old_weight = weights[courier.courier_type]
            new_weight = weights[request.json["courier_type"]]
            assert request.json["courier_type"] in ["foot", "bike", "car"]
            courier.courier_type = request.json["courier_type"]
            if old_weight > new_weight:
                wrong_orders.append(Order.query.filter_by(assigned_to=courier.courier_id).filter_by(completed=0).filter(Order.weight > new_weight).all())

        if "working_hours" in request.json.keys():
            assert request.json["working_hours"]
            orders = Order.query.filter_by(assigned_to=courier_id).filter_by(completed=0).all()
            order_ids = [order.order_id for order in orders]
            good_order = dict(zip(order_ids, [False] * len(order_ids)))
        for hour in courier["working_hours"]:
            start, end = hour.start_time, hour.end_time
            hours_to_commit = Courier_work_hours(hours=hours, courier_id=courier["courier_id"])
            db.session.add(hours_to_commit)
            delivers = Deli_hours.query.filter(Deli_hours.order_id.in_(order_ids)).all()
            for deli in delivers:
                if deli.start_time >= start and deli.start_time < end or deli.start_time <= start and deli.end_time > start:
                    good_order[deli.order_id] = True
            [wrong_orders.append(order) for order in orders if good_order[order.order_id]]

        for wr_order in wrong_orders:
            wr_order.assigned_to = 0

        db.session.commit()
    else:
        return ("Bad request", 400)


@app.route("/orders/assign", methods=["POST"])
def assign_orders():
    if not request.is_json:
        return abort (400, "Data format not json")
    if "courier_id" not in request.json.keys():
        return abort (400, "Courier was'nt sent")

    weights = {"foot": 1000, "bike": 1500, "car": 5000}
    courier = Courier.query.filter_by(courier_id=request.json["courier_id"]).all()
    result = {"orders" : []}

    if not courier:
        return abort (400)

    capacity = weights[courier[0].courier_type]
    cour_id = courier[0].courier_id
    regions = Courier_regions.query.filter_by(courier_id=cour_id).all()
    regions = [region.region for region in regions]
    hours = Courier_work_hours.query.filter_by(courier_id=cour_id).all()

    tmp = Order.query.filter_by(assigned_to=0).filter_by(completed=0)
    potential_orders = tmp.filter(Order.region.in_(regions)).filter(Order.weight <= capacity).all()
    po_ids = [po.order_id for po in potential_orders]

    orders_to_accept = set()

    for hour in hours:
        start, end = hour.start_time, hour.end_time
        delivers = Deli_hours.query.filter(Deli_hours.order_id.in_(po_ids)).all()
        for deli in delivers:
            if deli.start_time >= start and deli.start_time < end or deli.start_time <= start and deli.end_time > start:
                orders_to_accept = orders_to_accept.union(set([deli.order_id]))

    current_time = datetime.datetime.now().replace(microsecond=0).isoformat()

    orders = Order.query.filter(Order.order_id.in_(orders_to_accept)).all()
    for order in orders:
        result["orders"].append({"id" : order.order_id})
        order.assigned_to = cour_id
        order.cour_type = courier[0].courier_type
        order.assigned_when = current_time

    if result["orders"]:
        db.session.commit()
        result["assign_time"] = current_time
    return (result, 200)

@app.route("/orders/complete", methods=["POST"])
def complete_orders():
    if not request.is_json:
        return abort (400, "Data format not json")
    keys = set(request.json.keys())
    right_keys = set(["courier_id", "order_id", "complete_time"])
    if keys - right_keys or right_keys - keys:
        return abort (400)

    cour_id = request.json["courier_id"]
    orde_id = request.json["order_id"]
    order = Order.query.filter_by(comlpeted=0).filter_by(assigned_to=cour_id).filter_by(orter_id=orde_id).all()

    if not order:
        return ("Bad order request", 400)
    if True: #plz reploce me with try
        parser.parse(request.json["complete_time"])
    else:
        return ("Bad time format", 400)

    order[0].comlpeted = 1
    order[0].completed_when = request.json["complete_time"]
    db.session.commit()
    result = {"order_id" : orde_id}
    return (result, 200)


@app.route("/couriers/<courier_id>", methods=["GET"])
def get_courier(courier_id):
    return {404: "not implemented"}


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8080)