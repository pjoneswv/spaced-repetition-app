import PyPDF2
import re
import sqlite3
import json

def parse_pdf(pdf_path):
    print(f"Attempting to parse PDF at: {pdf_path}")
    questions = []
    current_question = None
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"Successfully opened PDF with {len(pdf_reader.pages)} pages")
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                print(f"\nProcessing page text: {text[:100]}...")  # Print first 100 chars
                
                lines = text.split('\n')
                
                for line in lines:
                    print(f"Processing line: {line[:50]}...")
                    
                    # Match "QUESTION X" or "Question X"
                    if re.match(r'^QUESTION\s+\d+|^Question\s+\d+', line, re.IGNORECASE):
                        if current_question:
                            questions.append(current_question)
                        current_question = {
                            'question': '',
                            'options': {},
                            'correct_answer': None,
                            'explanation': ''
                        }
                        continue
                    
                    # Capture the question text (lines before options)
                    if current_question and not current_question['question'] and not line.strip().startswith(('A.', 'B.', 'C.', 'D.', 'Answer:', 'Explanation:')):
                        current_question['question'] = line.strip()
                    
                    # Capture options
                    if line.strip().startswith(('A.', 'B.', 'C.', 'D.')):
                        option_letter = line[0]
                        option_text = line[2:].strip()
                        if current_question:
                            current_question['options'][option_letter] = option_text
                    
                    # Capture the answer (looking specifically for "Answer: X")
                    if line.strip().startswith('Answer:'):
                        if current_question:
                            answer_match = re.search(r'Answer:\s*([A-D])', line)
                            if answer_match:
                                current_question['correct_answer'] = answer_match.group(1)
                    
                    # Capture the explanation
                    if line.strip().startswith('Explanation:'):
                        if current_question:
                            current_question['explanation'] = line[12:].strip()
                    elif current_question and current_question.get('explanation'):
                        # Append additional explanation lines
                        current_question['explanation'] += ' ' + line.strip()
        
        # Add the last question
        if current_question:
            questions.append(current_question)
        
        # Debug output
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}:")
            print(f"Question text: {q['question'][:100]}...")
            print(f"Options: {q['options']}")
            print(f"Correct Answer: {q['correct_answer']}")
            print(f"Explanation: {q['explanation'][:100]}...")
        
        return questions
    
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return []

def update_database(questions):
    try:
        conn = sqlite3.connect('questions.db')
        cursor = conn.cursor()
        
        # Update existing questions with correct answers
        for i, question in enumerate(questions, 1):
            try:
                cursor.execute("""
                    UPDATE questions 
                    SET correct_answer = ?
                    WHERE id = ?
                """, (question['correct_answer'], i))
                
                print(f"Updated question {i} with correct answer: {question['correct_answer']}")
            except Exception as e:
                print(f"Error updating question {i}: {e}")
        
        conn.commit()
        conn.close()
        print("Database update completed successfully")
    
    except Exception as e:
        print(f"Database error: {e}")

def main():
    # Update this path to your PDF file location
    pdf_path = '/Users/pauljones/Desktop/Coding Applications/PDF App/your_pdf_file.pdf'
    
    print("Starting PDF parsing process...")
    print(f"Using PDF path: {pdf_path}")
    
    questions = parse_pdf(pdf_path)
    
    print(f"\nFound {len(questions)} questions")
    if questions:
        print("\nFirst question sample:")
        print(questions[0])
        
        print("\nUpdating database...")
        update_database(questions)
    else:
        print("No questions found in PDF")

if __name__ == "__main__":
    main()
