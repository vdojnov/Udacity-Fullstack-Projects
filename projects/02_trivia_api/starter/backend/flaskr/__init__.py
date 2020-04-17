# https://github.com/cmccarthy15/Workshop_Exercise/blob/master/Requests_Starter/backend/flaskr/__init__.py
# Vurtaul Env: .\env\Scripts\activate   and   deactivate

import os
from flask import Flask, request, abort, jsonify, url_for, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from  sqlalchemy.sql.expression import func, select

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
      categoriess = Category.query.all()
      catagories = [category.format() for category in categoriess]
      new_obj = {}
      for i in catagories:
          new_obj[i['id']] = i['type']

      result = jsonify({
        'success': True,
        "categories": new_obj
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

    catagories = [category.format() for category in categoriess]
    new_obj = {}
    for i in catagories:
        new_obj[i['id']] = i['type']

    # a = []
    # for i in catagories:
    #     new_obj = {}
    #     new_obj[i['id']] = i['type']
    #     a.append(new_obj)

    return jsonify ({
        'success': True,
        'questions': questions,
        'total_questions': total_questions,
        'categories': new_obj,
        'current_category': None
    })



  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_category_questions(cat_id):
      a = cat_id
      questions = Question.query.order_by(Question.id).filter(Question.category == int(a))
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
  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  def delete_questions(q_id):
      del_question = Question.query.filter(Question.id == int(q_id)).one_or_none()
      del_question.delete()

      # flash('There was an error trying to delete this questions')
      # db.session.rollback()

      page = request.args.get('page', 1, type=int)
      start = (page - 1 ) * QUESTIONS_PER_PAGE
      end = page * QUESTIONS_PER_PAGE
      questionss = Question.query.order_by(Question.id).all()
      questions = [que.format() for que in questionss][start:end]


      total_questions = len(questionss)
      categoriess = Category.query.all()
      catagories = [category.format() for category in categoriess]
      new_obj = {}
      for i in catagories:
          new_obj[i['id']] = i['type']

      return jsonify({
          'success': True,
          'questions': questions,
          'total_questions': total_questions,
          'categories': new_obj,
          'current_category': None

      })


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

  @app.route('/questions', methods=['POST'])
  def post_question():
      body = request.get_json()

      search_term = body.get('searchTerm', None)

      if search_term is not None:
          question = Question.query.filter(Question.question.ilike('%'+ search_term +'%'))
          q_formated = [que.format() for que in question]

          categoriess = Category.query.all()
          catagories = [category.format() for category in categoriess]
          new_obj = {}
          for i in catagories:
              new_obj[i['id']] = i['type']

          return jsonify({
          'success': True,
          'questions': q_formated
          })



      nquestion = body.get('question', None)
      nanswer = body.get('answer', None)
      ndifficulty = body.get('difficulty', None)
      ncategory = body.get('category', None)


      try:
          add_question = Question(question=nquestion, answer=nanswer, difficulty=ndifficulty, category=ncategory)
          add_question.insert()

          return jsonify({
            'success': True,
          })
      except:
          abort(422)

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  # done with the first get


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
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
      body = request.get_json()

      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)

     # TESTTTT
      # random_q = Question.query.order_by(func.random()).all()
      # # del random_q[0]

       # previous_questions = [10, 11]
       # quiz_category = {type: "click", id: '6'}
      # random_q = Question.query.order_by(func.random()).filter(Question.category == 6).all()



      if quiz_category['id'] == 0:
          random_q = Question.query.order_by(func.random()).all()
      else:
          random_q = Question.query.order_by(func.random()).filter(Question.category == int(quiz_category['id'])).all()


      if previous_questions:
          for question_id in previous_questions:
              repeated = Question.query.filter(Question.id == question_id).first()
              if repeated in random_q:
                  random_q.remove(repeated)

      if not random_q:
          result = False
      else:
          result = random_q[0].format()


      # 1. Choose where there is a category or not and create a list
      # 2. for the first one load all questions, then loop and remove all the questions in the list (if thing in some_list: some_list.remove(thing))


      return jsonify ({
        'question': result
        # 'question': [r.format() for r in random_q],
        # 'lenght': len([r.format() for r in random_q])
      })





  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  return app
