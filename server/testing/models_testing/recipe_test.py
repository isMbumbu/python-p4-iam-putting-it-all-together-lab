import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Tests for the Recipe model.'''

    def setup_method(self):
        '''Setup method to run before each test.'''
        with app.app_context():
            db.create_all()  # Create tables
            User.query.delete()  # Clear User table
            Recipe.query.delete()  # Clear Recipe table
            db.session.commit()

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        
        with app.app_context():
            # Create a new user for this test
            user = User(username="TestUser  ", _password_hash="hashed_password")
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id  # Use the created user's ID
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == """Or kind rest bred with am shed then. In""" + \
                """ raptures building an bringing be. Elderly is detract""" + \
                """ tedious assured private so to visited. Do travelling""" + \
                """ companions contrasted it. Mistress strongly remember""" + \
                """ up to. Ham him compass you proceed calling detract.""" + \
                """ Better of always missed we person mr. September""" + \
                """ smallness northward situation few her certainty""" + \
                """ something."""
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''
    
        with app.app_context():
            # Create a new user for this test
            user = User(username="TestUser  ", _password_hash="hashed_password")
            db.session.add(user)
            db.session.commit()

            # Create a recipe without a title
            recipe = Recipe(
                instructions="Some instructions that are long enough to pass validation.", 
                minutes_to_complete=30, 
                user_id=user.id  # Use the created user's ID
            )
            
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''requires instructions to be at least 50 characters long.'''
        
        with app.app_context():
            # Create a new user for this test
            user = User(username="TestUser  ", _password_hash="hashed_password")
            db.session.add(user)
            db.session.commit()
    
            # Attempt to create a recipe with instructions that are too short
            with pytest.raises(ValueError) as exc_info:
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="Short instructions",  # Less than 50 characters
                    minutes_to_complete=30,
                    user_id=user.id  # Use the created user's ID
                )
                db.session.add(recipe)
                db.session.commit()
            
            # Assert that the error message matches the expected validation rule
            assert str(exc_info.value) == "Instructions must be at least 50 characters long."