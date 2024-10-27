import sqlite3
import json
from datetime import datetime, timedelta
import random
import os

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # Create questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT
            )
        ''')
        
        # Create progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                question_id INTEGER PRIMARY KEY,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                correct_count INTEGER DEFAULT 0,
                incorrect_count INTEGER DEFAULT 0,
                consecutive_correct INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

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
        now = datetime.now()
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
        
        next_review = now + timedelta(days=days_until_review)
        
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

def get_question_stats(question_id):
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT correct_count, incorrect_count, consecutive_correct 
            FROM user_progress 
            WHERE question_id = ?
        ''', (question_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'correct_count': result[0],
                'incorrect_count': result[1],
                'consecutive_correct': result[2]
            }
        return {
            'correct_count': 0,
            'incorrect_count': 0,
            'consecutive_correct': 0
        }
        
    except Exception as e:
        print(f"Error getting question stats: {e}")
        return None

def create_progress_table():
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                question_id INTEGER PRIMARY KEY,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                correct_count INTEGER DEFAULT 0,
                incorrect_count INTEGER DEFAULT 0,
                consecutive_correct INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Progress table created successfully")
    except Exception as e:
        print(f"Error creating progress table: {e}")

# Create the progress table when this module is imported
create_progress_table()

def get_random_question():
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # First, check if we have any questions
        cursor.execute("SELECT COUNT(*) FROM questions")
        total_questions = cursor.fetchone()[0]
        print(f"DEBUG: Total questions in database: {total_questions}")
        
        if total_questions > 0:
            # Get a random question ID
            random_id = random.randint(1, total_questions)
            print(f"DEBUG: Selected random question ID: {random_id}")
            
            # Get the random question
            cursor.execute("""
                SELECT id, question, options, correct_answer, explanation 
                FROM questions 
                WHERE id = ?
            """, (random_id,))
            
            question = cursor.fetchone()
            conn.close()

            if question:
                question_data = {
                    'id': question[0],
                    'question': question[1],
                    'options': json.loads(question[2]),
                    'correct_answer': question[3],
                    'explanation': question[4]
                }
                print(f"DEBUG: Successfully loaded question {question_data['id']}")
                return question_data
            else:
                print(f"DEBUG: No question found with ID {random_id}")
        else:
            print("DEBUG: No questions in database")
        
        return None
    except Exception as e:
        print(f"DEBUG: Error in get_random_question: {e}")
        return None

def verify_database():
    """Verify database has questions and correct structure"""
    try:
        print("\nVerifying database...")
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Found tables: {[table[0] for table in tables]}")
        
        # Verify questions table exists
        if 'questions' not in [table[0] for table in tables]:
            print("ERROR: Questions table not found!")
            return False
        
        # Count questions
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        print(f"Number of questions in database: {count}")
        
        if count == 0:
            print("WARNING: No questions in database!")
            return False
            
        # Sample a question
        cursor.execute("SELECT * FROM questions LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print("\nSample question found:")
            print(f"ID: {sample[0]}")
            print(f"Question: {sample[1][:100]}...")
            print(f"Options: {sample[2]}")
            print(f"Answer: {sample[3]}")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"\nDatabase verification error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def clear_and_reload_database(pdf_path):
    """Clear and reload the database with questions from the specified PDF"""
    try:
        print(f"\nClearing and reloading database with PDF: {pdf_path}")
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS user_progress")
        cursor.execute("DROP TABLE IF EXISTS questions")
        
        # Recreate tables
        cursor.execute('''
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT,
                explanation TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE user_progress (
                question_id INTEGER PRIMARY KEY,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                correct_count INTEGER DEFAULT 0,
                incorrect_count INTEGER DEFAULT 0,
                consecutive_correct INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        ''')
        
        conn.commit()
        
        # Parse questions from the provided PDF
        from pdf_parser import parse_pdf
        questions = parse_pdf(pdf_path)
        
        if questions:
            valid_questions = 0
            skipped_questions = 0
            
            for question in questions:
                if question.get('correct_answer'):
                    try:
                        cursor.execute('''
                            INSERT INTO questions 
                            (question, options, correct_answer, explanation)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            question['question'],
                            json.dumps(question['options']),
                            question['correct_answer'],
                            question.get('explanation', '')
                        ))
                        valid_questions += 1
                    except Exception as e:
                        print(f"Error inserting question: {e}")
                else:
                    skipped_questions += 1
            
            conn.commit()
            conn.close()
            print(f"\nSuccessfully loaded {valid_questions} questions")
            if skipped_questions > 0:
                print(f"Skipped {skipped_questions} questions due to missing answers")
            return True
        else:
            print("No questions were parsed from the PDF")
            return False
            
    except Exception as e:
        print(f"Error during database reload: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def verify_pdf_path(pdf_path):
    """Verify the PDF file exists"""
    if os.path.exists(pdf_path):
        print(f"Found PDF file: {pdf_path}")
        return True
    else:
        print(f"PDF file not found at: {pdf_path}")
        return False

