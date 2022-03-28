import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
✅TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
!TODO implement endpoint
    ✅GET /drinks
        ✅it should be a public endpoint
        ✅it should contain only the drink.short() data representation
    ✅returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    if dinks is None:
        abort(404)
    return jsonify ({
        'success': True,
        'drinks': drinks,
    })


'''
!TODO implement endpoint
    ✅GET /drinks-detail
        ✅it should require the 'get:drinks-detail' permission
        ✅it should contain the drink.long() data representation
    ✅returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth("get:drinks-detail")
def drinks_detail(token):
    drinks = list(map(Drink.long, Drink.query.all()))
    if drinks in None:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks,
    })


'''
✅TODO implement endpoint
    ✅POST /drinks
        ✅it should create a new row in the drinks table
        ✅it should require the 'post:drinks' permission
        ✅it should contain the drink.long() data representation
    ✅returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
# drink row in models.py is as the following: Drink(title:"", recipe:"[{name, color, parts}]") and then insert


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(token):
    new_drink_data = json.loads(request.data.decode('utf-8'))
    new_drink = Drink(title=new_drink_data['title'], recipe=json.dumps(
        new_drink_data['recipe']))
    try:
        Drink.insert(new_drink)
        drinks = list(map(Drink.long, Drink.query.all()))
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(500)


'''
✅TODO implement endpoint
    ✅PATCH /drinks/<id>
        ✅where <id> is the existing model id
        ✅it should respond with a 404 error if <id> is not found
        ✅it should update the corresponding row for <id>
        ✅it should require the 'patch:drinks' permission
        ✅it should contain the drink.long() data representation
    ✅returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>/', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title:
        drink.title = title
    if recipe:
        for ingredient in recipe:
            name = ingredient.get('name', None)
            color = ingredient.get('color', None)
            parts = ingredient.get('parts', None)
            if not name or color or parts:
                abort(400)
        drink.recipe = json.dumps(recipe)
    try:
        drink.update()
        drinks = list(map(Drink.long, Drink.query.all()))
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(500)



'''
✅TODO implement endpoint
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
def deleteDrinks(token, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        db.session.rollback()
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
!TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
✅TODO implement error handler for 404
    error handler should conform to general task above
'''
#errors: ✅400, ✅404, ✅422, ✅500

@app.errorhandler(400)
def badRequest(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden request"
    }), 403 

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def internalServerError(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


'''
✅TODO implement error handler for AuthError
    error handler should conform to general task above

'''
@app.errorhandler(AuthError)
def handling_AuthError(exception):
    res = jsonify(exception.error)
    res.status_code = exception
