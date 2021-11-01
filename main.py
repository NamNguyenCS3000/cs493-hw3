from google.cloud import datastore
from flask import Flask, request
import json
import constants

app = Flask(__name__)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /slips to use this API"\

@app.route('/boats', methods=['POST','GET'])
def boats_get_post():
    content = request.get_json()
    if request.method == 'POST':
        if "name" in content and "type" in content and "length" in content:
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            client.put(new_boat)
            boat_key = client.key(constants.boats, new_boat.key.id)
            boat = client.get(key=boat_key)
            boat["id"] = new_boat.key.id
            boat["self"] = str(request.url_root) + 'boats/' + str(new_boat.key.id)
            return json.dumps(boat), 201
        else:
            return json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results)
    else:
        return 'Method not recognized'

@app.route('/boats/<id>', methods=['PUT','PATCH','DELETE','GET'])
def boats_put_patch_delete(id):
    content = request.get_json()
    boat_key = client.key(constants.boats, int(id))
    boat = client.get(key=boat_key)
    if request.method == "PUT":
        boat.update({"name": content["name"], "description": content["description"]})
        client.put(boat)
        return '', 204
    elif request.method == 'PATCH':
        if "name" in content and "type" in content and "length" in content:
            if boat_key != None and boat != None:
                boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
                client.put(boat)
                boat["id"] = boat.key.id
                boat["self"] = str(request.url_root) + 'boats/' + str(boat.key.id)
                return json.dumps(boat), 200
            else:
                return json.dumps({"Error": "No boat with this boat_id exists"}), 404
        else:
            return json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400
    elif request.method == 'DELETE':
        if boat_key != None and boat != None:
            client.delete(boat_key)
            query = client.query(kind=constants.slips)
            results = list(query.fetch())
            for e in results:
                try:
                    slipsCurrentBoat = e["current_boat"]
                    if int(slipsCurrentBoat) != None and slipsCurrentBoat == int(id):
                        print(f"slip (e): {e}")
                        print(f"this boat is still assigned to slip {e.key.id}")
                        slip = client.get(key=e.key)
                        print(f"slip (slip): {slip}")
                        slip.update({"number": e["number"], "current_boat": None})
                        print(f"slip (slip updated): {slip}")
                        client.put (slip)
                        slip = client.get(key=e.key)
                        print(f"slip (slip after put): {slip}")
                except:
                    continue
            return '', 204
        else:
            return json.dumps({"Error": "No boat with this boat_id exists"}), 404
    elif request.method == 'GET':
        if boat_key != None and boat != None:
            boat["id"] = boat.key.id
            boat["self"] = str(request.url_root) + 'boats/' + str(boat.key.id)
            return json.dumps(boat), 200
        else:
            return json.dumps({"Error": "No boat with this boat_id exists"}), 404
    else:
        return 'Method not recognized'

@app.route('/slips', methods=['POST','GET'])
def slips_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if "number" in content:
            new_slip = datastore.entity.Entity(key=client.key(constants.slips))
            new_slip.update({"number": content["number"], "current_boat": None})
            client.put(new_slip)
            slip_key = client.key(constants.slips, new_slip.key.id)
            slip = client.get(key=slip_key)
            slip["id"] = new_slip.key.id
            slip["self"] = str(request.url_root) + 'slips/' + str(new_slip.key.id)
            return json.dumps(slip), 201
        else:
            return json.dumps({"Error": "The request object is missing the required number"}), 400
    elif request.method == 'GET':
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results)
    else:
        return 'Method not recognized'

@app.route('/slips/<id>', methods=['DELETE','GET'])
def slips_delete_get(id):
    slip_key = client.key(constants.slips, int(id))
    slip = client.get(key=slip_key)
    if request.method == 'DELETE':
        if slip_key != None and slip != None:
            client.delete(slip_key)
            return '', 204
        else:
            return json.dumps({"Error": "No slip with this slip_id exists"}), 404
    elif request.method == 'GET':
        if slip_key != None and slip != None:
            slip["id"] = slip.key.id
            slip["self"] = str(request.url_root) + 'slips/' + str(slip.key.id)
            return json.dumps(slip), 200
        else:
            return json.dumps({"Error": "No slip with this slip_id exists"}), 404
    else:
        return 'Method not recognized'

@app.route('/slips/<slip_id>/<boat_id>', methods=['PUT', 'DELETE'])
def slips_boats_put_delete(slip_id, boat_id):
    slip_key = client.key(constants.slips, int(slip_id))
    slip = client.get(key=slip_key)
    if request.method == 'PUT':
        if slip_key != None and slip != None:
            slipsCurrentBoat = slip["current_boat"]
            boat_key = client.key(constants.boats, int(boat_id))
            boat = client.get(key=boat_key)
            if boat != None:
                query = client.query(kind=constants.slips)
                results = list(query.fetch())
                for e in results:
                    try:
                        slipsCurrentBoat = e["current_boat"]
                        if int(slipsCurrentBoat) != None and slipsCurrentBoat == int(boat_id):
                            print(f"Bad Request: this boat has the current slip {e.key.id}")
                    except:
                        continue
            else:
                return json.dumps({"Error": "The specified boat and/or slip does not exist"}), 404
            if slip["current_boat"] != None:
                return json.dumps({"Error": "The slip is not empty"}), 403
        else:
            return json.dumps({"Error": "The specified boat and/or slip does not exist"}), 404
        slip.update({"number": slip["number"], "current_boat": int(boat_id)})
        client.put(slip)
        return '',204
    elif request.method == 'DELETE':
        if slip_key != None and slip != None:
            slipsCurrentBoat = slip["current_boat"]
            if slipsCurrentBoat != None and int(slipsCurrentBoat) == int(boat_id):
                slip.update({"number": slip["number"], "current_boat": None})
                client.put(slip)
                return '', 204
            else:
                return json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404
        else:
            return json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404
    else:
        return 'Method not recognized'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
