import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    
    # Drop the existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS questions")
    
    # Create the table with the correct structure
    cursor.execute('''
    CREATE TABLE questions (
        id INTEGER PRIMARY KEY,
        question TEXT,
        options TEXT,
        correct_answer TEXT,
        explanation TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized with the correct structure.")

def check_and_update_db():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    
    # Check if the 'options' column exists
    cursor.execute("PRAGMA table_info(questions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'options' not in columns:
        # If 'options' column doesn't exist, we need to update the table
        cursor.execute('''
        ALTER TABLE questions
        ADD COLUMN options TEXT
        ''')
        conn.commit()
        print("Database schema updated.")
    
    conn.close()

def add_question(question_dict):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO questions (question, options, correct_answer, explanation)
    VALUES (?, ?, ?, ?)
    ''', (question_dict['question'], json.dumps(question_dict['options']), 
          question_dict['correct_answer'], question_dict['explanation']))
    conn.commit()
    conn.close()

def get_question(question_id):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    query = "SELECT * FROM questions WHERE id = ?"
    print(f"Executing SQL query: {query} with id {question_id}")
    cursor.execute(query, (question_id,))
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

def update_question_difficulty(question_id, difficulty, next_review):
    conn = sqlite3.connect('questions.db')
    c = conn.cursor()
    c.execute("UPDATE questions SET difficulty = ?, next_review = ? WHERE id = ?", (difficulty, next_review, question_id))
    conn.commit()
    conn.close()

def get_total_questions():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_question_number(question_id):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions WHERE id <= ?", (question_id,))
    number = cursor.fetchone()[0]
    conn.close()
    return number

def clear_questions():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions")
    conn.commit()
    conn.close()
    print("Cleared all questions from the database")
