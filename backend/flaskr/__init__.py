import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

db = SQLAlchemy()

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={'/': {'origins': '*'}})
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    # GET categories route
    @app.route("/categories", methods=["GET"])
    def get_all_categories():
        if request.method == "GET":
            categories = Category.query.order_by(Category.id).all()
            my_cat = {}

            for cat in categories:
                my_cat[cat.id] = cat.type

            if len(my_cat) == 0:
                abort(404)

            return jsonify({
                'categories': my_cat,
                'success': True
            })
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
    # GET Question use pagination

    @app.route('/questions', methods=['GET'])
    def get_questions():
        if request.method == "GET":
            questions = Question.query.all()
            paginated_questions = paginate_questions(request, questions)

            if len(paginated_questions) == 0:
                abort(404)
            
            categories = Category.query.all()
            my_cat = {}

            for cat in categories:
                my_cat[cat.id] = cat.type

            return jsonify({
                'success': True,
                'total_questions': len(questions),
                'categories': my_cat,
                'questions': paginated_questions
            })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    # DELETE question
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        if request.method == "DELETE":
            q = Question.query.filter_by(id=id).one_or_none()
            if q is None:
                abort(404)

            q.delete()
            return jsonify({
                'deleted': id,
                'success': True,
                'total_questions': len(Question.query.all())
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

    # Create question POST METHOD
    @app.route('/questions', methods=['POST'])
    def create_a_question():
        if request.method == "POST":
            body = request.get_json()
            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category',  None)
            
            searchTerm = body.get('searchTerm', None)
            try:
                if searchTerm:
                    questions = Question.query.filter(Question.question.ilike(f"%{searchTerm}%")).all()
                    paginated_questions = paginate_questions(request, questions)
                    
                    return jsonify({
                        'success': True,
                        'questions': paginated_questions,
                        'total_questions': len(paginated_questions)
                    })

                else:
                    q = Question(question=question, answer=answer, difficulty=difficulty, category=category)
                    q.insert()

                    questions = Question.query.order_by(Question.id).all()
                    paginated_questions = paginate_questions(request, questions)

                    return jsonify({
                        'success': True,
                        'question_created': q.question,
                        'created': q.id,
                        'questions': paginated_questions,
                        'total_questions': len(Question.query.all())
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
    # GET questions by a category
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        if request.method == "GET":
            category = Category.query.filter_by(id=category_id).one_or_none()
            if category is None:
                abort(404)
            try:
                questions = Question.query.filter_by(category=category.id).all()
                paginated_questions = paginate_questions(request, questions)

                return jsonify({
                    'success': True,
                    'total_questions': len(Question.query.all()),
                    'current_category': category.type,
                    'questions': paginated_questions
                })

            except:
                abort(400)
        

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

    @app.route('/play', methods=['POST'])
    def play_game():
        if request.method == "POST":
            try:
                body = request.get_json()
                prev_questions = body.get('previous_questions', None)
                category = body.get('quiz_category', None)

                cat_id = category['id']
                next_question = None
                
                if cat_id != 0:
                    av_questions = Question.query.filter_by(category=cat_id).filter(Question.id.notin_((prev_questions))).all()    
                else:
                    av_questions = Question.query.filter(Question.id.notin_((prev_questions))).all()
                
                if len(av_questions) > 0:
                    next_question = random.choice(av_questions).format()
                
                return jsonify({
                    'question': next_question,
                    'success': True,
                })
            except:
                abort(422)


    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 422

    return app

    