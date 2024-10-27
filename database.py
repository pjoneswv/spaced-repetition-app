import sqlite3
import json
import random
from datetime import datetime

def get_question(question_id):
    print(f"Executing SQL query: SELECT * FROM questions WHERE id = ? with id {question_id}")
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        question = cursor.fetchone()
        conn.close()

        if question:
            return {
                'id': question[0],
                'question': question[1],
                'options': json.loads(question[2]),
                'correct_answer': question[3],  # Make sure this column exists
                'explanation': question[4]
            }
        return None
    except Exception as e:
        print(f"Error fetching question: {e}")
        return None

def get_random_question():
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # Get total number of questions
        cursor.execute("SELECT COUNT(*) FROM questions")
        total_questions = cursor.fetchone()[0]
        
        if total_questions > 0:
            # Get a random question ID
            random_id = random.randint(1, total_questions)
            
            # Get the random question
            cursor.execute("SELECT * FROM questions WHERE id = ?", (random_id,))
            question = cursor.fetchone()
            conn.close()

            if question:
                return {
                    'id': question[0],
                    'question': question[1],
                    'options': json.loads(question[2]),
                    'correct_answer': question[3],
                    'explanation': question[4]
                }
        return None
    except Exception as e:
        print(f"Error fetching random question: {e}")
        return None

def create_tables():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    
    # Add user_progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            question_id INTEGER,
            last_reviewed TIMESTAMP,
            next_review TIMESTAMP,
            correct_count INTEGER DEFAULT 0,
            incorrect_count INTEGER DEFAULT 0,
            consecutive_correct INTEGER DEFAULT 0,
            PRIMARY KEY (question_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def update_question_progress(question_id, is_correct):
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # Get current progress
        cursor.execute('''
            SELECT correct_count, incorrect_count, consecutive_correct 
            FROM user_progress 
            WHERE question_id = ?
        ''', (question_id,))
        
        result = cursor.fetchone()
        if result:
            correct_count, incorrect_count, consecutive_correct = result
        else:
            correct_count = incorrect_count = consecutive_correct = 0
        
        # Calculate next review time based on performance
        now = datetime.datetime.now()
        if is_correct:
            correct_count += 1
            consecutive_correct += 1
            # Exponential backoff for correct answers
            days_until_review = min(2 ** consecutive_correct, 30)
        else:
            incorrect_count += 1
            consecutive_correct = 0
            # Review incorrect questions sooner
            days_until_review = 1
        
        next_review = now + datetime.timedelta(days=days_until_review)
        
        # Update or insert progress
        cursor.execute('''
            INSERT OR REPLACE INTO user_progress 
            (question_id, last_reviewed, next_review, correct_count, 
             incorrect_count, consecutive_correct)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (question_id, now, next_review, correct_count, 
              incorrect_count, consecutive_correct))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error updating question progress: {e}")

def get_next_question():
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        now = datetime.datetime.now()
        
        # First, try to get questions due for review
        cursor.execute('''
            SELECT q.id, q.question, q.options, q.correct_answer, q.explanation,
                   COALESCE(up.correct_count, 0) as correct_count,
                   COALESCE(up.incorrect_count, 0) as incorrect_count
            FROM questions q
            LEFT JOIN user_progress up ON q.id = up.question_id
            WHERE up.next_review IS NULL 
               OR up.next_review <= ?
            ORDER BY 
                CASE 
                    WHEN up.next_review IS NULL THEN 1
                    ELSE 2
                END,
                RANDOM()
            LIMIT 1
        ''', (now,))
        
        question = cursor.fetchone()
        conn.close()
        
        if question:
            return {
                'id': question[0],
                'question': question[1],
                'options': json.loads(question[2]),
                'correct_answer': question[3],
                'explanation': question[4],
                'stats': {
                    'correct_count': question[5],
                    'incorrect_count': question[6]
                }
            }
        return None
        
    except Exception as e:
        print(f"Error getting next question: {e}")
        return None
