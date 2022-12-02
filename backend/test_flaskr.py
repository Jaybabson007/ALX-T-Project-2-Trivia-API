import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from DB_settings import DB_TEST_NAME, DB_TEST_USER


from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_TEST_NAME
        self.database_path = "postgresql://{}@{}/{}".format(DB_TEST_USER,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test 1: GET all available categories
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))


    # Test 2: GET all question including pagination (every 10 questions)
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # Test 3: GET 404 for retrieving questions beyond valid page
    def test_404_requesting_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    # Test 4: DELETE question based on question id
    def test_delete_question(self):
        # create a new question to be deleted
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()

        # get the id of the new question
        question_id = question.id

        # delete the question and store response
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        # see if the question has been deleted
        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        #check status code and success message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    # Test 5: DELETE question that doesn't exists
    def test_delete_question_that_does_not_exists(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
    #Test 6: POST a new question
    def test_create_new_question(self):
        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        total_questions_before = len(Question.query.all())
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        total_questions_after = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)

    # Test 7: question unprocessable 422 ERROR
    def test_422_add_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["message"], "unprocessable")

    #Test 8:get back question filtered by search term
    def test_search_question_by_term(self):
        res = self.client().post('/questions/search', json={'search': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 2)

    # Test 9: get empty list of questions when search term doesn't retrieve any question
    def test_404_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    #Test 10: get questions based on one category
    def test_get_questions_by_category(self):

        # send request with category id 1 for science
        response = self.client().get('/categories/1/questions')

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that questions are returned (len != 0)
        self.assertNotEqual(len(data['questions']), 0)

        # check that current category returned is science
        self.assertEqual(data['current_category'], 'Science')
    
    # Test 11: get 404 error when categories doesn't exists
    def test_get_paginated_questions_for_non_existing_category(self):
        res = self.client().get('/categories/88/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")

    # Test 12: get quiz by category or all questions
    def test_get_quiz_by_category_or_all(self):
        questions_params = {
            'previous_questions': [17, 18],
            'quiz_category': {'id': 1, 'type': 'Science'}
        }

        res = self.client().post('/quizzes', json=questions_params)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['previous_questions'])
        self.assertTrue(data['question'])

    # Test 13: get quiz without parameter
    def test_404_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()