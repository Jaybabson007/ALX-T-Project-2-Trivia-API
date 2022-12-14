import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# For pagination of retrieved question from the DB based on number of question per page
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

"""
code for creating helper function inspired by the github repo github.com/alikhoudar
"""

#Helper function to get category type based on given list of categories and category id
def get_category_type(categories, category_id):
    for category in categories:
        if category['id'] == category_id:
            return category['type']


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        return response


    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():

            # get all categories and add to dictionary
            categories = Category.query.all()
            categories_dictionary = {}
            for category in categories:
                categories_dictionary[category.id] = category.type

            # abort 404 if no categories found
            if (len(categories_dictionary) == 0):
                abort(404)

            # return data to view
            return jsonify({
                'success': True,
                'categories': categories_dictionary
            })



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        
        # get all questions and paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # get all categories and add to dictionary
        categories = Category.query.all()
        categories_dictionary = {}
        for category in categories:
            categories_dictionary[category.id] = category.type

        # abort 404 if no questions
        if (len(current_questions) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dictionary
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id=id).one_or_none
            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all
            currentQuestions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception as e:
            print(e)
            abort(404)
    

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def create_new_question():
        #get request
        body = request.get_json()

        #get new data
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        #Add new question
        try:
            
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()

            #Update the view
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_question_by_term():
        body = request.get_json()
        search_term = body.get('search', None)

        try:
            if search_term:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(search_term))
                ).all()

                if len(selection) > 0:
                    current_questions = paginate_questions(request, selection)
                    categories = [category.format() for category in Category.query.order_by(Category.id).all()]

                    return jsonify({
                        'success': True,
                        'questions': current_questions,
                        'total_questions': len(current_questions),
                        'current_category': get_category_type(categories, current_questions[0]['category'])
                    })
                else:
                    return jsonify({
                        'success': True,
                        'questions': [],
                        'total_questions': 0,
                        'current_category': ""
                    })
        except:
             abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        
        # get the category by id
        category = Category.query.filter_by(id=id).one_or_none()

        # abort 400 for bad request if category isn't found
        if (category is None):
            abort(400)

        # get the matching questions
        selection = Question.query.filter_by(category=category.id).all()

        # paginate the selection
        paginated = paginate_questions(request, selection)

        # return the results
        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_quizzes_by_category_or_all():

        try:                
            body = request.get_json()
            previous_questions = body.get("previous_questions",None)
            quiz_category = body.get("quiz_category",None)

            # Check if quiz_category exists
            if quiz_category:
                if quiz_category['id']== 0:
                    question = Question.query.order_by(Question.id).filter(
                Question.id.notin_(previous_questions)).first()
                else:
                    question = Question.query.order_by(Question.id).filter(
                Question.id.notin_(previous_questions)).filter(Question.category == quiz_category['id']).first()

                if previous_questions is None:
                    previous_questions = []

                if question:
                    previous_questions.append(question.id)
                
                return jsonify({
                    "success": True,
                    "previous_questions" : previous_questions,
                    "question" : question.format() if question else question
                })
        except:
            abort(422)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({
                'success': False,
                'error': 400,
                'message': 'bad request'
            }), 400
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                'success': False,
                'error': 404,
                'message': 'resource not found'
            }), 404
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def bad_request(error):
        return (
            jsonify({
                'success': False,
                'error': 500,
                'message': 'internal server error'
            }), 500
        )

    return app

