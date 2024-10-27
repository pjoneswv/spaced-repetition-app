import PyPDF2
import re
from utils import log_error, log_info
from pypdf import PdfReader

def extract_questions_from_pdf(pdf_path):
    print(f"Opening PDF file: {pdf_path}")
    questions = []
    try:
        reader = PdfReader(pdf_path)
        print(f"PDF has {len(reader.pages)} pages")
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        
        print(f"Extracted {len(text)} characters of text")
        
        # Improved question extraction
        question_pattern = r'QUESTION\s+\d+[\s\S]*?(?=QUESTION\s+\d+|\Z)'
        raw_questions = re.findall(question_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for raw_question in raw_questions:
            question_dict = parse_question(raw_question)
            if question_dict:
                questions.append(question_dict)
        
        print(f"Extracted {len(questions)} questions")
    except FileNotFoundError:
        log_error(f"PDF file not found: {pdf_path}")
    except PyPDF2.errors.PdfReadError:
        log_error(f"Error reading PDF file: {pdf_path}")
    except Exception as e:
        log_error(f"Unexpected error processing PDF {pdf_path}: {str(e)}")
        print(f"Error processing PDF: {str(e)}")
    
    return questions

def parse_question(raw_question):
    # Remove the "QUESTION X" prefix
    question_text = re.sub(r'^QUESTION\s+\d+\s*', '', raw_question, flags=re.IGNORECASE).strip()
    
    # Split the question into its components
    parts = re.split(r'\nAnswer:\s*[A-Z]\s*\n', question_text, maxsplit=1)
    if len(parts) != 2:
        return None
    
    question_and_options, answer_and_explanation = parts
    
    # Extract options
    options_pattern = r'([A-Z])\.\s*(.*?)(?=\n[A-Z]\.|$)'
    options = dict(re.findall(options_pattern, question_and_options, re.DOTALL))
    
    # Extract the question text (everything before the first option)
    question_text = re.split(r'\n[A-Z]\.', question_and_options)[0].strip()
    
    # Extract correct answer and explanation
    correct_answer = answer_and_explanation[0]
    explanation = answer_and_explanation[1:].strip()
    
    return {
        'question': question_text,
        'options': options,
        'correct_answer': correct_answer,
        'explanation': explanation
    }
