import sqlite3
import json

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
