from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime
from sqlalchemy import func



load_dotenv()  # Load environment variables
# Add this near the top of your file
QUESTION_RECOMMENDATIONS = {
    'A1': {
            1: "Consider sensory training exercises to help manage auditory sensitivity. This might include gradual exposure to different environments with varying noise levels.",
            0: "Your normal auditory processing is a strength. Continue to maintain balanced sensory environments."
        },
        'A2': {
            1: "Practice focusing on details through activities like puzzles or detailed artwork to balance your tendency to see the whole picture.",
            0: "Work on seeing the bigger picture through activities that require holistic thinking like strategic games or system mapping."
        },
        'A3': {
            1: "Your ability to multitask is a strength. Continue to utilize this in your daily activities.",
            0: "Practice single-tasking with full attention, then gradually introduce secondary tasks to improve multitasking abilities."
        },
        'A4': {
            1: "Your ability to resume tasks after interruption is a strength. Continue to apply this skill in structured environments.",
            0: "Practice task-switching exercises and use techniques like pomodoro method to build task resumption skills."
        },
        'A5': {
            1: "Continue to leverage your ability to understand implied meanings in communication.",
            0: "Consider practicing contextual interpretation through reading literary texts with metaphors and discussing them with others."
        },
        'A6': {
            1: "Your social attentiveness is a strength. Continue to observe and respond to social cues.",
            0: "Practice recognizing boredom signals through social skills training or by watching and analyzing social interactions in media."
        },
        'A7': {
            1: "Work with a therapist on theory of mind exercises to better understand others' intentions.",
            0: "Your ability to understand others' intentions is a strength. Continue to use this in social situations."
        },
        'A8': {
            1: "Consider structured social activities based on your interests to practice friendship-building skills.",
            0: "Your social connection skills are a strength. Continue to use these skills to build and maintain relationships."
        },
        'A9': {
            1: "Your enjoyment of social occasions is a strength. Continue to engage in social activities that you find pleasant.",
            0: "Start with small, structured social interactions in environments where you feel comfortable, gradually expanding your comfort zone."
        },
        'A10': {
            1: "Consider emotion recognition training or working with a therapist on empathy-building exercises.",
            0: "Your emotional intelligence is a strength. Continue to apply this in your interpersonal relationships."
        }
}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Add this right after your db = SQLAlchemy(app) line
with app.app_context():
    db.create_all()
login_manager = LoginManager(app)
login_manager.login_view = 'login'



# User model for database
class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
class TestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer)
    result = db.Column(db.String(20))  # 'Positive' or 'Negative'
    
    # Relationship
    user = db.relationship('User', backref='test_attempts')

class TestAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempt.id'))
    question_id = db.Column(db.Integer)
    answer = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='test_answers')
    attempt = db.relationship('TestAttempt', backref='answers')
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        age = request.form['age']
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken!', 'error')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(full_name=full_name, age=age, username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/test-intro')
@login_required
def test_intro():
    return render_template('test_intro.html')

@app.route('/demographics', methods=['GET', 'POST'])
@login_required
def demographics():
    if request.method == 'POST':
        # Process demographic data
        gender = request.form.get('gender')
        jaundice = request.form.get('jaundice') == 'yes'
        autism_family = request.form.get('autism_family') == 'yes'
        relation = request.form.get('relation')
        
        # You can store these in session or database if needed
        # For now, we'll just proceed to questions
        
        return redirect(url_for('question', q_num=1))
    
    return render_template('demographics.html')

@app.route('/question/<int:q_num>', methods=['GET', 'POST'])
@login_required
def question(q_num):

    questions = {
        1: 'Does the person speak very little and give unrelated answers to questions?',
        2: 'Does the person not respond to their name or avoid eye contact?',
        3: 'Does the person not engage in games of pretend with other children?',
        4: 'Does the person struggle to understand other people’s feelings?',
        5: 'Is the person easily upset by small changes?',
        6: 'Does the person have obsessive interests?',
        7: 'Is the person over or under-sensitive to smells, tastes,or touch?',
        8: 'Does the person struggle to socialize with other children?',
        9: 'Does the person avoid physical contact?',
        10: 'Does the person show little awareness of dangerous situations?'
    }

    # Ensure valid question number
    if q_num < 1 or q_num > 10:
        flash('Invalid question number', 'error')
        return redirect(url_for('dashboard'))
    
    # Handle form submission
    if request.method == 'POST':
        try:
            answer = int(request.form.get('answer', 0))
            new_answer = TestAnswer(
                user_id=current_user.id,
                question_id=q_num,
                answer=answer
            )
            db.session.add(new_answer)
            db.session.commit()
            
            if q_num == 10:
                return redirect(url_for('results'))
            return redirect(url_for('question', q_num=q_num+1))
        except Exception as e:
            db.session.rollback()
            flash('Error saving your answer', 'error')
            return redirect(url_for('question', q_num=q_num))
    
    # Render question page
    return render_template('question.html',
                        question_text=questions[q_num],
                         question_num=q_num,
                         progress=q_num*10)

@app.route('/results')
@login_required
def results():
    # Get all answers for this user's latest test
    answers = TestAnswer.query.filter_by(
        user_id=current_user.id
    ).order_by(TestAnswer.timestamp.desc()).limit(10).all()
    
    # Calculate score
    score = sum(answer.answer for answer in answers) * 10
    result = "Positive" if score >= 70 else "Negative"
    
    # Generate question-specific recommendations
    question_recommendations = []
    for answer in answers:
        question_id = f"A{answer.question_id}"
        if question_id in QUESTION_RECOMMENDATIONS:
            rec = QUESTION_RECOMMENDATIONS[question_id][answer.answer]
            question_recommendations.append({
                'question': f"Question {answer.question_id}",
                'answer': "Agree" if answer.answer == 1 else "Disagree",
                'recommendation': rec
            })
    
    # Generate overall recommendations
    if score >= 80:
        general_recommendations = [
            "Consider professional evaluation.",
            "Your answers suggest very high probability of Autism."
        ]
    elif (score <80 and score >=50):
        general_recommendations = [
            "Your results suggest typical characteristics.",
            "Continue monitoring if concerned."
        ]
    else :
        general_recommendations = [
            "Your results suggest that probability of Autism is low, still can take medical advice.",
        ]
    
    # Save test attempt
    # Create test attempt record
    new_attempt = TestAttempt(
        user_id=current_user.id,
        score=score,
        result=result
    )
    db.session.add(new_attempt)
    db.session.commit()
    
    # Associate answers with this attempt
    for answer in answers:
        answer.attempt_id = new_attempt.id
    db.session.commit()
    
    return render_template('results.html',
                         score=score,
                         result=result,
                         question_recommendations=question_recommendations,
                         general_recommendations=general_recommendations)

@app.route('/history')
@login_required
def history():
    # Get all test attempts with their answers
    attempts = TestAttempt.query.filter_by(
        user_id=current_user.id
    ).options(
        db.joinedload(TestAttempt.answers)
    ).order_by(TestAttempt.timestamp.desc()).all()
    
    return render_template('history.html',
                         attempts=attempts,
                         test_count=len(attempts))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)