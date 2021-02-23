import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:root@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        self.new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }

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

    # test get categories
    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    # test get questions

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)


    # test get questions with a wrong page parameter

    def test_get_questions_404(self):
        response = self.client().get('/questions?page=2000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    # test delete a question with id 2
    def test_delete_question(self):
        response = self.client().delete('/questions/2')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'],2)

    
    # test detele a questions with a id that is not in the database
    def test_delete_question_404(self):
        response = self.client().delete('/questions/5000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)


    # test create question

    def test_create_question(self):
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_question_creation_not_allowed(self):
        response = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')


    # test search with results

    def test_search(self):
        response = self.client().post('/questions', json={'searchTerm': 'invented'})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_without_results(self):
        response = self.client().post('/questions', json={'searchTerm':'asdf'})

        data = json.loads(response.data)

        self.assertEqual(data['total_questions'],0)
        self.assertEqual(data['success'], True)
    

    # test get questions by category
    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['current_category'], 'Science')
        self.assertEqual(data['success'], True)

    def test_get_404_questions_by_category(self):
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['success'], False)

    # test quiz
    def test_quiz(self):
        quiz_round = {'previous_questions': [], 'quiz_category': {'type': 'Geography', 'id': 14}}
        response = self.client().post('/play', json=quiz_round)
        data = json.loads(response.data)

        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_quiz(self):
        response = self.client().post('/play', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()