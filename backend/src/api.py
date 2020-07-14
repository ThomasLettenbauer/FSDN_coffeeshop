import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import logging

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    return response


# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    mydrinks = [drink.short() for drink in drinks]

    print('*** mydrinks ***')
    print(mydrinks)

    return jsonify({
        'success': True,
        'drinks': mydrinks
    })
    # except:
    #    abort(401)


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinksdetail(payload):
    try:
        drinks = Drink.query.all()

        mydrinks = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': mydrinks
        })
    except:
        abort(401)


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def postDrink(payload):
    try:
        title = request.get_json()['title']
        recipe = request.get_json()['recipe']
        newdrink = Drink(title=title,
                         recipe=json.dumps(recipe))
        newdrink.insert()
        return jsonify({
            'success': True,
            'drinks': [newdrink.long()]
        })
    except Exception:
        abort(400)


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patchDrink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        request_json = request.get_json()

        if 'title' in request_json:
            drink.title = request_json['title']

        if 'recipe' in request_json:
            drink.recipe = json.dumps(request_json['recipe'])

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        abort(400)


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'deleted': id
        })

    except Exception:
        abort(422)


# Error Handling
'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(400)
def not_found(error):
    return jsonify({

        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(403)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 404


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500
