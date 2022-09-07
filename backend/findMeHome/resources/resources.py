from backend.findMeHome.dl_model.DLModel import breedPredict, model
from backend.findMeHome.models.main import DBHandler
from backend.findMeHome.models.shelter import Shelter
from backend.findMeHome.models.user import User
from backend.findMeHome.models.dog import Dog
from backend.findMeHome.models.diseasedog import Diseasedog
from flask_restful import Resource
from flask import request, Response, jsonify, make_response, session

db = DBHandler()

class signUpApi(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        if data.get("user") is not None:
            user = data["user"]
            # use db to create
            if data["user"].get("type") == "adopter":
                adp =User(user.get("fname"),user.get("lname"),user.get("city"),user.get("country"),user.get("email"),user.get("username"),
                          user.get("password"),user.get("picture"),user.get("phone"))
                status, msg = db.add(adp)
            elif data["user"].get("type") == "shelter":
                shelter = Shelter(None, user["street"], user["city"], user["country"], user["email"], user["username"],
                                  user["password"], None, None, None)
                status, msg = db.add(shelter)
            if data["user"].get("type") == "adopter" or data["user"].get("type") == "shelter":
                if status:
                    return make_response(jsonify("Sign up Successfull"), 201)
                else:
                    return make_response(jsonify(msg), 412)

            else:
                return "Invalid User type", 412
        else:
            return "Invalid Data posted", 412

#Recieves username and password
#Returns Id of user if login was successfull
#Returns faiure code otherwise
class signInApi(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        #if there is no data for key user in json return failure
        if data.get("user") is None:
            return "Invalid Data posted", 412
        try:
            user = data["user"]
            if user.get("username") is None or user.get("password") is None:
                return "Couldn't login. Please try again", 412
            #call sign in function of db
            status, user = db.signIn(user.get("username"), user.get("password"))
            if status is True:
                session["userName"] = user.username
                return make_response(jsonify(user.username)), 200
            else:
                return "Couldn't login. Please try again", 412
        except:
            return "Couldn't login. Please try again", 412

#user.username
#dog.name
#dog.age
#dog.imageURL
#dog.bid
#dog.diseasesId
#dog.diseaseDescription (one description)

class dogApi(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        if data.get("user") is None or data.get("dog") is None:
            return "Invalid Data posted", 412
        if session.get(data.get("user").get("username")) is None:
            return "Shelter not logged in", 412

        try:
           # Create a dog object
           dog = Dog(data.get("user").get("id"), data.get("dog").get("name"), data.get("dog").get("age")
                     , data.get("dog").get("bid"), data.get("dog").get("imgURL"))

           # add dog to db
           status, result = db.add(dog)
           # if add operation failed
           if status is False:
               return make_response(jsonify(result), 412)
           # if add operation succeeded
           diseases = data.get("diseases")
           if diseases is not None:
               for diseaseId in diseases:
                   dogDisease = Diseasedog(data.get("dog").get("dieseaseDescription"), result.did,
                                           diseaseId)

           return make_response(jsonify("Dog added Successfully"), 200)
        except:
            return "Couldn't add dog. Please try again", 412
#

class ModelApi(Resource):
    @staticmethod
    def post():
        url = request.get_json()
        if url.get('dogURL') is None:
            return "Invalid Data posted", 412
        res = breedPredict(url['dogURL'], model)
        return make_response(jsonify(res), 200)
