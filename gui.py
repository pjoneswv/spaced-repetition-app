import tkinter as tk
from tkinter import filedialog, ttk
from pdf_processor import extract_questions_from_pdf
from database_manager import add_question, get_question, get_total_questions, get_question_number, clear_questions, update_question_progress, get_question_stats
from database import get_random_question  # Add this import at the top
import json

class QuestionApp:
    def __init__(self, master):
        self.master = master
        master.title("CompTIA Security+ Practice Questions")
        
        # Create main container
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create and pack the question label
        self.question_label = ttk.Label(
            self.main_frame, 
            wraplength=600, 
            justify="left",
            padding="10"
        )
        self.question_label.pack(fill=tk.X, pady=10)
        
        # Create frame for options
        self.options_frame = ttk.Frame(self.main_frame)
        self.options_frame.pack(fill=tk.X, pady=10)
        
        # Create submit button
        self.submit_button = ttk.Button(
            self.main_frame,
            text="Submit Answer",
            command=self.submit_answer
        )
        self.submit_button.pack(pady=10)
        
        # Create feedback label
        self.feedback_label = ttk.Label(
            self.main_frame,
            wraplength=600,
            justify="left"
        )
        self.feedback_label.pack(fill=tk.X, pady=10)
        
        # Create next question button (hidden initially)
        self.next_question_button = ttk.Button(
            self.main_frame,
            text="Next Question",
            command=lambda: self.load_question()
        )
        
        # Initialize state variables
        self.current_question_id = None
        self.answer_submitted = False
        self.user_answer = tk.StringVar()
        
        # Progress tracking
        self.progress_label = ttk.Label(
            self.main_frame,
            text="Progress: 0 correct, 0 incorrect"
        )
        self.progress_label.pack(pady=10)
        
        # Load first question
        self.load_question()
        
    def resize_window(self):
        """Resize window to fit content"""
        self.master.update_idletasks()
        width = self.master.winfo_reqwidth()
        height = self.master.winfo_reqheight()
        self.master.geometry(f"{width}x{height}")

    def submit_answer(self):
        if not self.answer_submitted:
            user_answer = self.user_answer.get()
            if user_answer:
                question_data = get_question(self.current_question_id)
                if not question_data:
                    self.feedback_label.config(text="Error: Could not load question data")
                    return
                
                options = question_data.get('options', {})
                explanation = question_data.get('explanation', '')
                correct_answer = question_data.get('correct_answer')
                
                if not correct_answer:
                    self.feedback_label.config(text="Error: No correct answer available for this question")
                    return
                
                is_correct = user_answer == correct_answer
                
                # Update progress in database
                update_question_progress(self.current_question_id, is_correct)
                
                if is_correct:
                    result = "Correct!"
                else:
                    result = "Incorrect."

                correct_option_text = options.get(correct_answer, "Answer not available")
                feedback = f"{result}\n\nThe correct answer is: {correct_answer}. {correct_option_text}\n\nExplanation:\n{explanation}"
                
                # Add progress information to feedback
                stats = get_question_stats(self.current_question_id)
                if stats:
                    feedback += f"\n\nYour progress on this question:"
                    feedback += f"\nCorrect: {stats['correct_count']}"
                    feedback += f"\nIncorrect: {stats['incorrect_count']}"
                
                self.feedback_label.config(text=feedback)
                self.answer_submitted = True
                self.submit_button.config(state=tk.DISABLED)
                self.next_question_button.pack(pady=10)
                
            else:
                self.feedback_label.config(text="Please select an answer before submitting.")
        else:
            print("Answer already submitted")

        self.master.update_idletasks()
        self.resize_window()

    def display_question(self, question_data):
        print(f"\nDEBUG: Displaying question")
        print(f"DEBUG: Question text: {question_data.get('question', 'No question available')}")
        print(f"DEBUG: Options: {question_data.get('options', {})}")
        print(f"DEBUG: Correct answer: {question_data.get('correct_answer', 'No answer specified')}")
        
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(tk.END, question_data.get('question', 'No question text available'), "center")
        self.question_text.config(state=tk.DISABLED)

        # Clear previous options
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Reset the current answer
        self.current_answer.set("")

        # Display options
        options = question_data.get('options', {})
        if not options:
            print("WARNING: No options available for this question")
            
        for letter, text in options.items():
            print(f"DEBUG: Creating option {letter}: {text}")
            option_frame = ttk.Frame(self.options_frame)
            option_frame.pack(fill=tk.X, pady=5)
            
            radio = ttk.Radiobutton(option_frame, 
                                   variable=self.current_answer, 
                                   value=letter,
                                   command=self.update_user_answer)
            radio.pack(side=tk.LEFT, padx=(0, 10))
            
            label = ttk.Label(option_frame, text=f"{letter}. {text}", wraplength=500)
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.submit_button.config(state=tk.NORMAL)
        self.feedback_label.config(text="")
        
        print("DEBUG: Question display completed")
        self.update_progress()

    def next_question(self):
        print("Next question button clicked")
        if self.current_question_id is not None:
            next_id = self.current_question_id + 1
            self.load_question(next_id)
        self._configure_scroll_region()

    def load_question(self, question_id=None):
        """Load a random question"""
        try:
            # Get a random question
            question_data = get_random_question()
            
            if question_data:
                self.current_question_id = question_data['id']
                
                # Update the question display
                self.question_label.config(text=question_data['question'])
                
                # Clear previous options
                for widget in self.options_frame.winfo_children():
                    widget.destroy()
                
                # Create new radio buttons for options
                self.user_answer = tk.StringVar()
                for letter, text in question_data['options'].items():
                    option = ttk.Radiobutton(
                        self.options_frame,
                        text=f"{letter}. {text}",
                        value=letter,
                        variable=self.user_answer
                    )
                    option.pack(anchor='w', pady=5)
                
                # Reset submit button and feedback
                self.submit_button.config(state=tk.NORMAL)
                self.feedback_label.config(text="")
                self.answer_submitted = False
                
                # Hide next question button until answer is submitted
                self.next_question_button.pack_forget()
                
                print(f"DEBUG: Question {self.current_question_id} loaded successfully")
            else:
                print("DEBUG: No question data returned")
                
        except Exception as e:
            print(f"DEBUG: Error loading question: {e}")

    def display_question(self, question_data):
        print(f"\nDEBUG: Displaying question")
        print(f"DEBUG: Question text: {question_data.get('question', 'No question available')}")
        print(f"DEBUG: Options: {question_data.get('options', {})}")
        print(f"DEBUG: Correct answer: {question_data.get('correct_answer', 'No answer specified')}")
        
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(tk.END, question_data.get('question', 'No question text available'), "center")
        self.question_text.config(state=tk.DISABLED)

        # Clear previous options
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Reset the current answer
        self.current_answer.set("")

        # Display options
        options = question_data.get('options', {})
        if not options:
            print("WARNING: No options available for this question")
            
        for letter, text in options.items():
            print(f"DEBUG: Creating option {letter}: {text}")
            option_frame = ttk.Frame(self.options_frame)
            option_frame.pack(fill=tk.X, pady=5)
            
            radio = ttk.Radiobutton(option_frame, 
                                   variable=self.current_answer, 
                                   value=letter,
                                   command=self.update_user_answer)
            radio.pack(side=tk.LEFT, padx=(0, 10))
            
            label = ttk.Label(option_frame, text=f"{letter}. {text}", wraplength=500)
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.submit_button.config(state=tk.NORMAL)
        self.feedback_label.config(text="")
        
        print("DEBUG: Question display completed")
        self.update_progress()

    def clear_feedback(self):
        self.feedback_label.config(text="")

    def update_progress(self):
        total = get_total_questions()
        if self.current_question_id is None:
            self.progress_label.config(text=f"No questions loaded. Total questions: {total}")
        else:
            self.progress_label.config(text=f"Question {self.current_question_id} of {total}")

    def clear_gui(self):
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.config(state=tk.DISABLED)
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.feedback_label.config(text="")
        self.progress_label.config(text="")
        self.next_question_button.pack_forget()
        self._configure_scroll_region()

    def display_initial_state(self):
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(tk.END, "Please upload a PDF to start.", "center")
        self.question_text.config(state=tk.DISABLED)
        self.update_progress()
        self._configure_scroll_region()

    def upload_pdf(self):
        self.clear_gui()
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            clear_questions()
            questions = extract_questions_from_pdf(file_path)
            print(f"Extracted {len(questions)} questions")
            for i, question in enumerate(questions):
                if all(key in question for key in ['question', 'options', 'correct_answer', 'explanation']):
                    add_question(question)
                    print(f"Added question {i+1}")
                else:
                    print(f"Skipping invalid question {i+1}: {question}")
            total_questions = get_total_questions()
            if total_questions > 0:
                self.load_question(1)
            else:
                print("No questions were added to the database")
            self._configure_scroll_region()

    def update_user_answer(self):
        self.user_answer.set(self.current_answer.get())
        print(f"DEBUG: User selected answer: {self.user_answer.get()}")

    def fix_question_data(self, question_data):
        correct_answer = question_data['correct_answer']
        options = question_data['options']
        explanation = question_data.get('explanation', '').lower()

        if correct_answer not in options:
            print(f"WARNING: Correct answer '{correct_answer}' not in options. Attempting to fix.")
            # Try to find the correct answer based on the explanation
            for option, text in options.items():
                if text.lower().strip() in explanation:
                    question_data['correct_answer'] = option
                    print(f"Fixed: New correct answer is '{option}'")
                    return question_data

            # If we can't find a match, add the correct answer to the options
            options[correct_answer] = "Added option"
            print(f"Added missing option '{correct_answer}' to options")

        return question_data





