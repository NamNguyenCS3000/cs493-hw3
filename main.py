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
    if request.method == 'POST':
        content = request.get_json()
        if ("name" in content and "type" in content and "length" in content):
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            # None ~= Null in python
            new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            print(new_boat) # <Entity('boats', 5746980898734080) {'number': 1}>
            client.put(new_boat)
            # putResult = client.put(new_boat) # print(putResult) == "None"
            # query = client.query(kind=constants.boats)
            # results = list(query.fetch())
            
            # boat_num = new_boat['number']
            # print(str(boat_num)) # == 1
            boat_key = client.key(constants.boats, new_boat.key.id)
            print(str(boat_key))
            boat = client.get(key=boat_key)
            
            boat["id"] = new_boat.key.id
            boat["self"] = str(request.url_root) + 'boats/' + str(new_boat.key.id)
            return (json.dumps(boat), 201)
        else:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
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
    if request.method == 'PATCH':
        content = request.get_json()
        if ("name" in content and "type" in content and "length" in content):
            boat_key = client.key(constants.boats, int(id))
            if (boat_key != None):
                boat = client.get(key=boat_key)
                if (boat != None):
                    boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
                    client.put(boat)
                    boat["id"] = boat.key.id
                    boat["self"] = str(request.url_root) + 'boats/' + str(boat.key.id)
                    return (json.dumps(boat), 200)
                else:
                    return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
            else:
                return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
        else:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
    # elif request.method == 'PUT':
    #     content = request.get_json()
    #     boat_key = client.key(constants.boats, int(id))
    #     boat = client.get(key=boat_key)
    #     boat.update({"name": content["name"], "description": content["description"]})
    #     client.put(boat)
    #     return ('',200)
    elif request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        if (boat_key != None):
            boat = client.get(key=boat_key)
            if (boat != None):
                client.delete(boat_key)

                query = client.query(kind=constants.slips)
                results = list(query.fetch())
                for e in results:
                    # print(f"slip: {e}")
                    try:
                        slipsCurrentBoat = e["current_boat"]
                        if (int(slipsCurrentBoat) != None and slipsCurrentBoat == int(id)):
                            print(f"slip (e): {e}")
                            print(f"this boat is still assigned to slip {e.key.id}")

                            # slip_key = client.key(constants.slips, int(slip_id))
                            # # errorMsg = "The specified boat and/or slip does not exist"
                            # if (slip_key != None):
                            #     slip = client.get(key=slip_key)
                            #     # print(f"slip: {slip}")
                            #     # slipsCurrentBoat = slip["current_boat"]
                            #     # print(f"slipsCurrentBoat: {slipsCurrentBoat}")
                            #     if (slip != None):
                            
                            slip = client.get(key=e.key)
                            print(f"slip (slip): {slip}")
                            slip.update({"number": e["number"], "current_boat": None})
                            print(f"slip (slip updated): {slip}")
                            client.put (slip)
                            slip = client.get(key=e.key)
                            print(f"slip (slip after put): {slip}")
                            # return (json.dumps({"Error": f"Bad Request, this boat is assigned to slip {e.key.id}"}), 400)
                    except:
                        continue

                return ('', 204)
            else:
                return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
        else:
            return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
    elif request.method == 'GET':
        boat_key = client.key(constants.boats, int(id))
        if (boat_key != None):
            boat = client.get(key=boat_key)
            if (boat != None):
                boat["id"] = boat.key.id
                boat["self"] = str(request.url_root) + 'boats/' + str(boat.key.id)
                return (json.dumps(boat), 200)
            else:
                return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
        else:
            return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
    else:
        return 'Method not recognized'

@app.route('/slips', methods=['POST','GET'])
def slips_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if "number" in content:
            new_slip = datastore.entity.Entity(key=client.key(constants.slips))
            # None ~= Null in python
            new_slip.update({"number": content["number"], "current_boat": None})
            print(new_slip) # <Entity('slips', 5746980898734080) {'number': 1}>
            client.put(new_slip)
            # putResult = client.put(new_slip) # print(putResult) == "None"
            # query = client.query(kind=constants.slips)
            # results = list(query.fetch())
            
            # slip_num = new_slip['number']
            # print(str(slip_num)) # == 1
            slip_key = client.key(constants.slips, new_slip.key.id)
            print(str(slip_key))
            slip = client.get(key=slip_key)
            
            slip["id"] = new_slip.key.id
            slip["self"] = str(request.url_root) + 'slips/' + str(new_slip.key.id)
            return (json.dumps(slip), 201)
        else:
            return (json.dumps({"Error": "The request object is missing the required number"}), 400)
    elif request.method == 'GET':
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            # print(f"slip: {e}")
            # try:
            #     slipsCurrentBoat = e["current_boat"]
            #     if (slipsCurrentBoat == None):
            #         e["current_boat"] = None
            # except:
            #     e["current_boat"] = None
        return json.dumps(results)
    else:
        return 'Method not recognized'

@app.route('/slips/<id>', methods=['PUT','DELETE','GET'])
def slips_put_delete(id):
    # if request.method == 'PUT':
    #     content = request.get_json()
    #     slip_key = client.key(constants.slips, int(id))
    #     slip = client.get(key=slip_key)
    #     slip.update({"number": content["number"], "current_boat": content["current_boat"]})
    #     client.put(slip)
    #     return ('',200)
    if request.method == 'DELETE':
        slip_key = client.key(constants.slips, int(id))
        if (slip_key != None):
            slip = client.get(key=slip_key)
            if (slip != None):
                client.delete(slip_key)
                return ('', 204)
            else:
                return (json.dumps({"Error": "No slip with this slip_id exists"}), 404)
        else:
            return (json.dumps({"Error": "No slip with this slip_id exists"}), 404)
    elif request.method == 'GET':
        slip_key = client.key(constants.slips, int(id))
        if (slip_key != None):
            slip = client.get(key=slip_key)
            if (slip != None):
                slip["id"] = slip.key.id
                slip["self"] = str(request.url_root) + 'slips/' + str(slip.key.id)
                # print(f"slip: {slip}")
                # try:
                #     slipsCurrentBoat = slip["current_boat"]
                #     if (slipsCurrentBoat == None):
                #         slip["current_boat"] = None
                # except:
                #     slip["current_boat"] = None
                return (json.dumps(slip), 200)
            else:
                return (json.dumps({"Error": "No slip with this slip_id exists"}), 404)
        else:
            return (json.dumps({"Error": "No slip with this slip_id exists"}), 404)
    else:
        return 'Method not recognized'

@app.route('/slips/<slip_id>/<boat_id>', methods=['PUT', 'DELETE'])
def slips_boats_put(slip_id, boat_id):
    if request.method == 'PUT':
        slip_key = client.key(constants.slips, int(slip_id))
        # errorMsg = "The specified boat and/or slip does not exist"
        if (slip_key != None):
            slip = client.get(key=slip_key)
            # print(f"slip: {slip}")
            # slipsCurrentBoat = slip["current_boat"]
            # print(f"slipsCurrentBoat: {slipsCurrentBoat}")
            if (slip != None):
                slipsCurrentBoat = slip["current_boat"]
                # print(f"current boat: {slipsCurrentBoat}")
                boat_key = client.key(constants.boats, int(boat_id))
                # if (boat_key != None):
                boat = client.get(key=boat_key)
                # print(f"boat: {boat}")
                if (boat != None):
                    # make sure boat is not assigned to another slip
                    # this doesn't actually work in all cases, esp. when current_boat is null, the results don't have the current_boat
                    # may need to make a separate call to get the current_boat in this case
                    query = client.query(kind=constants.slips)
                    results = list(query.fetch())
                    for e in results:
                        # print(f"slip: {e}")
                        try:
                            slipsCurrentBoat = e["current_boat"]
                            if (int(slipsCurrentBoat) != None and slipsCurrentBoat == int(boat_id)):
                                print(f"Bad Request, this boat is assigned to slip {e.key.id}")
                                # return (json.dumps({"Error": f"Bad Request, this boat is assigned to slip {e.key.id}"}), 400)
                        except:
                            continue
                else:
                    return (json.dumps({"Error": "The specified boat and/or slip does not exist"}), 404)
                # else:
                #     return (json.dumps({"Error": "boat key messed The specified boat and/or slip does not exist"}), 404)
                if (slip["current_boat"] != None):
                    # print(str(slip["current_boat"]))
                    return (json.dumps({"Error": "The slip is not empty"}), 403)
            else:
                return (json.dumps({"Error": "The specified boat and/or slip does not exist"}), 404)
        else:
            return (json.dumps({"Error": "The specified boat and/or slip does not exist"}), 404)
        
        slip.update({"number": slip["number"], "current_boat": int(boat_id)})
        client.put(slip)
        return ('',204)
    elif request.method == 'DELETE':
        slip_key = client.key(constants.slips, int(slip_id))
        # errorMsg = "The specified boat and/or slip does not exist"
        if (slip_key != None):
            slip = client.get(key=slip_key)
            if (slip != None):
                try:
                    slipsCurrentBoat = slip["current_boat"]
                    if (slipsCurrentBoat != None):
                        if (int(slipsCurrentBoat) == int(boat_id)):
                            slip.update({"number": slip["number"], "current_boat": None})
                            client.put(slip)
                            return ('', 204)
                        else:
                            return (json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404)
                    else:
                        return (json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404)
                except:
                    return (json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404)
            else:
                return (json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404)
        else:
            return (json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404)
    else:
        return 'Method not recognized'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
