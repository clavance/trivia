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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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


    def test_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200, 'Expected status 200')

    '''
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''

    def test_pagination(self):
        res = self.client().get('questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(len(data['questions']), 10, 'Should be 10 questions per page')

    def test_nonexistent_page(self):
        res = self.client().get('/questions/?page=10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404, 'Expected status 404')

    '''
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    def test_questions_in_category(self):
        res = self.client().get('categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200, 'Expected status 200')
        self.assertTrue(data['questions'])

    def test_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200, 'Expected status 200')

    '''
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''

    def test_create_question(self):
        data = {
            'question': 'Who won the Premier League?',
            'answer': 'Liverpool',
            'category': 3,
            'difficulty': 1
        }
        res = self.client().post('/questions', json = data)
        self.assertEqual(res.status_code, 200, 'Failed to execute POST')

    '''
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    def test_delete_question(self):
        body = {'searchTerm': 'League'}
        res = self.client().post('/search', json=body)
        data = json.loads(res.data)
        id = int(data['questions'][-1]['id'])
        del_res = self.client().delete(f'/questions/{id}')
        self.assertEqual(del_res.status_code, 200, 'Failed to execute DELETE')

    '''
      TEST: Search by any phrase. The questions list will update to include
      only question that include that string within their question.
      Try using the word "title" to start.
    '''

    def test_search(self):
        body = {'searchTerm': 'title'}
        res = self.client().post('/search', json=body)
        data = json.loads(res.data)
        self.assertTrue((len(data['questions'])), '1')

    '''
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    def test_play(self):
        body= {
            'quiz_category':{
                'id': 1
            },
            'previous_questions': []
        }
        res = self.client().post('/quizzes', json=body)
        data = json.loads(res.data)
        self.assertEqual((data['category']), 1, 'Category does not match')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
