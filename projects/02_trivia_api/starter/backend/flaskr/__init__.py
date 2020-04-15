# https://github.com/cmccarthy15/Workshop_Exercise/blob/master/Requests_Starter/backend/flaskr/__init__.py
# Vurtaul Env: .\env\Scripts\activate   and   deactivate

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def get_catagories():
      categories = Category.query.all()

      result = jsonify({
        'success': True,
        "categories": [category.type for category in categories]
      })

      return result



  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''


  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1 ) * QUESTIONS_PER_PAGE
    end = page * QUESTIONS_PER_PAGE
    questionss = Question.query.all()
    questions = [que.format() for que in questionss][start:end]

    categoriess = Category.query.all()
    total_questions = len(questionss)
    catagories = [category.type for category in categoriess]
    # a = []
    # for i in catagories:
    #     new_obj = {}
    #     new_obj[i['id']] = i['type']
    #     a.append(new_obj)

    return jsonify ({
        'success': True,
        'questions': questions,
        'total_questions': total_questions,
        'categories': catagories,
        'current_category': None
    })



  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_category_questions(cat_id):
      a = cat_id + 1
      questions = Question.query.filter(Question.category == int(a))
      q_formated = [q.format() for q in questions]
      current_cat = Category.query.get(int(a))
      cat = Category.query.all()
      all_cat = [c.type for c in cat]


      return jsonify({
      'questions': [q.format() for q in questions],
      'total_questions': len(q_formated),
      'current_category': current_cat.format()
      })


  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''


  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  return app
