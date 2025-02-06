#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask import jsonify
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return {'error': 'Username and password are required'}, 422

        if User.query.filter(User.username == data['username']).first():
            return {'error': 'Username already exists'}, 422

        try:
            user = User(
                username=data['username'],
                bio=data.get('bio', ''),
                image_url=data.get('image_url', '')
            )
            user.password_hash = data['password']

            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'Failed to create user due to database constraints'}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        return {
            'id': user.id,
            'username': user.username,
            'image_url': user.image_url,
            'bio': user.bio
        }, 200

class Login(Resource):
    def post(self):
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return {'error': 'Username and password are required'}, 401

        user = User.query.filter(User.username == data['username']).first()

        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if 'user_id' not in session or session['user_id'] is None:
            return {"error": "No active session"}, 401  # Return 401 if no session
        
        session.pop('user_id', None)  # Remove the session
        return {"message": "Successfully logged out"}, 200  # Return 200 on success
    
 
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.all()
        recipes_data = [{
            'id': recipe.id,
            'title': recipe.title,
            'instructions': recipe.instructions,
            'minutes_to_complete': recipe.minutes_to_complete,
            'user': {
                'id': recipe.user.id,
                'username': recipe.user.username,
                'image_url': recipe.user.image_url,
                'bio': recipe.user.bio
            }
        } for recipe in recipes]

        return recipes_data, 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()

        if not data or not data.get('title') or not data.get('instructions') or not data.get('minutes_to_complete'):
            return {'error': 'Title, instructions, and minutes_to_complete are required'}, 422

        if len(data['instructions']) < 50:
            return {'error': 'Instructions must be at least 50 characters long'}, 422

        try:
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=user_id
            )

            db.session.add(recipe)
            db.session.commit()

            return {
                'id': recipe.id,
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'id': recipe.user.id,
                    'username': recipe.user.username,
                    'image_url': recipe.user.image_url,
                    'bio': recipe.user.bio
                }
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'Failed to create recipe due to database constraints'}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)