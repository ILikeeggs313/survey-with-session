from flask import Flask, render_template, session, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey
from flask import flash
from surveys import Question as question

#for this new improved app, we use session so it can remember the state of the survey

app = Flask(__name__)
#toolbar is only enabled in debug mode:
app.debug = True
#set a secret key to work with Flask sessions
app.config['SECRET_KEY'] = '123456789'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)


#empty list var resp to store people's answers in
RESPONSES = "responses"

#function to handle the first request
@app.route('/home')
def go_homepage():
    """Select a survey"""
    return render_template('home.html', survey = survey)

#redirect to question 0
#need a post methods to access the form
@app.route('/begin', methods =['GET'])
def begin_survey():
    """To begin the survey, clearing any flask session"""
    session[RESPONSES] = []
    return redirect('/questions/0', question = question)


#building a function to handle questions, with POST methods
@app.route('/answer', methods = ['POST'])
def handle_questions():
    """Save current response, showing radio options, and moving to the next
    question"""
    #to get the response from the form
    resp_choice = request.form['answer']

    #add the resp_choice to the Flask session
    responses = session[RESPONSES]

    #step four: handling answers, appending the answers to the resp list
    responses.append(resp_choice)
    session[RESPONSES] = responses

    # step 5 :if all the questions are answered, thank the user
    #len of the responses should equal the len of the list
    if(len(responses) == len(survey.questions)):
        return redirect('/thank-you')
    else:
        #return them back to the correct url
        return redirect(f'/questions/{len(responses)}')

@app.route('/questions/<int:qid>')
def show_questions(qid):
    """Show the cur questions"""
    responses = session.get(RESPONSES)
    if(responses is None):
        #accessing the question page too soon will redirect to home
        return redirect('/home')
    if(len(responses) == len(survey.questions)):
        return redirect('/thank-you')
    #to tackle the issue in step six: protecting questions
    if(len(responses) != qid):
        flash(f'invalid question id:{qid}')
        return redirect(f'/questions/{len(responses)}')
    question = survey.questions[qid]
    return render_template('question.html', question_num = qid,
    question = question)

#thank you route after the survey is completed
@app.route('/thank-you')
def complete_survey():
    """Survey is completed, show the thank you page."""
    return render_template('thank-you.html', survey = survey)

