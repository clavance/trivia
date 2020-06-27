import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

'''
Helper function for pagination
'''
def paginate(request, questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  formatted_questions = [question.format() for question in questions]
  return formatted_questions[start:end]


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  Set up CORS, allowing all origins
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  Set up CORS headers for after request
  '''
  @app.after_request
  def add_cors(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response

  '''
  Get all questions by categories
  '''
  @app.route('/categories', methods=['GET'])
  def get_questions_by_category():
    categories = Category.query.all()
    formatted_category = {category.id: category.type for category in categories}

    return jsonify({
    'success': True,
      'categories': formatted_category,
      'status': 200
      })

  '''
  Display all questions
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions =  Question.query.order_by(Question.id).all()
    categories = Category.query.order_by(Category.type).all()
    formatted_categories = {category.id: category.type for category in categories}
    current_questions = paginate(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': Question.query.count(),
      'categories': formatted_categories,
      'current_category': None
    })


  '''
  Delete question using ID
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    Question.query.get(id).delete()
    return jsonify({
      'success': True
    })

  '''
  Post a question
  '''
  @app.route('/questions', methods=['POST'])
  def add_questions():
    question = request.get_json()

    if not question['question']:
      error = "Enter a question"
      abort(500)

    try:
      Question(
        question=question['question'],
        answer=question['answer'],
        category=question['category'],
        difficulty=question['difficulty']
        ).insert()

      return jsonify({
          'question': question,
          'success': True,
          'status': 200
        })

    except:
        abort(422)

  '''
  Get questions by search term
  '''
  @app.route('/search', methods=['POST'])
  def search():
   search_term = request.get_json()['searchTerm']
   search_data = Question.query.filter(Question.question.ilike(f'%{search_term}%'))

   return jsonify({
     'questions': [q.format() for q in search_data],
     'current_category': None
   })


  '''
  Get questions based on category
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    questions = Question.query.filter_by(category=category_id).all()

    formatted_questions = [question.format() for question in questions]

    if len(formatted_questions) == 0:
      abort(404)

    return jsonify({
      'questions': formatted_questions,
      'total_questions': len(formatted_questions),
      'current_category': category_id
    })

  '''
  Get questions to play the quiz
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
    category = int(request.get_json()['quiz_category']['id'])
    questions = request.get_json()['previous_questions']

    if category == 0:
      unique_questions = Question.query.all()

    else:
      unique_questions = Question.query.filter_by(category=category).filter(Question.id.notin_(questions)).all()

    if len(unique_questions) > 0:
      return jsonify({
        'success': True,
        'question': random.choice([q.format() for q in unique_questions]),
        'category': category,
        'previous': [u.question for u in unique_questions]
      })

    else:
      return jsonify({
        'success': True,
        'question': None
      })

  '''
  Error handlers
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
        "error": 400,
        "success": False,
        "message": "bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        "error": 404,
        "success": False,
        "message": "not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "error": 422,
        "success": False,
        "message": "unprocessable"
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
        "error": 500,
        "success": False,
        "message": "internal server error"
      }), 500

  return app
