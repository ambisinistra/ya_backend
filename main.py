from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)


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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)