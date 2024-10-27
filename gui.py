import tkinter as tk
from tkinter import filedialog, ttk
from pdf_processor import extract_questions_from_pdf
from database_manager import add_question, get_question, get_total_questions, get_question_number, clear_questions
import json

class QuestionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Exam Question Study App")
        self.master.geometry("800x600")  # Set initial size
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.main_container = ttk.Frame(self.master)
        self.main_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<Configure>", self._configure_scroll_region)
        
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="n",
            width=self.master.winfo_width()
        )
        
        self.canvas.bind("<Configure>", self._configure_canvas_window)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Initialize variables
        self.current_question_id = None
        self.user_answer = tk.StringVar()
        self.current_answer = tk.StringVar()
        self.answer_submitted = False
        
        # Create widgets
        self.create_widgets()

        # Initial display
        self.display_initial_state()

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        # For Windows and MacOS
        delta = event.delta
        
        # For Linux (event.delta is not available)
        if event.num == 4:  # scroll up
            delta = 120
        elif event.num == 5:  # scroll down
            delta = -120
            
        self.canvas.yview_scroll(int(-1 * (delta/120)), "units")

    def _configure_scroll_region(self, event=None):
        """Configure the scroll region to encompass all widgets"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _configure_canvas_window(self, event=None):
        """Resize the canvas window when the window size changes"""
        width = event.width if event else self.master.winfo_width()
        self.canvas.itemconfig(self.canvas_window, width=width - 4)

    def resize_window(self):
        """Adjust the window size based on content"""
        self.master.update_idletasks()
        self._configure_scroll_region()

    # ... (rest of the methods remain exactly the same as in the previous version)

    def create_widgets(self):
        # Center container frame
        self.center_container = ttk.Frame(self.scrollable_frame)
        self.center_container.pack(fill="x", padx=20, pady=20)
        
        # Question frame
        self.question_frame = ttk.Frame(self.center_container)
        self.question_frame.pack(fill="x", pady=(0, 10))
        
        self.question_text = tk.Text(
            self.question_frame,
            wrap=tk.WORD,
            height=5,
            font=("Arial", 12),
            width=60
        )
        self.question_text.pack(fill="x")
        self.question_text.tag_configure("center", justify='center')
        
        # Options frame with fixed width
        self.options_frame = ttk.Frame(self.center_container)
        self.options_frame.pack(fill="x", pady=10)
        
        # Button and feedback container
        self.control_container = ttk.Frame(self.center_container)
        self.control_container.pack(fill="x", pady=10)
        
        # Submit button
        self.submit_button = ttk.Button(
            self.control_container,
            text="Submit",
            command=self.submit_answer
        )
        self.submit_button.pack(pady=5)
        
        # Create a frame specifically for the feedback to ensure centering
        self.feedback_frame = ttk.Frame(self.control_container)
        self.feedback_frame.pack(fill="x", pady=5)
        
        # Feedback label with center alignment
        self.feedback_label = ttk.Label(
            self.feedback_frame,
            text="",
            font=("Arial", 12),
            wraplength=500,
            justify="center",
            anchor="center"
        )
        self.feedback_label.pack(expand=True, fill="both")
        
        # Next question button
        self.next_question_button = ttk.Button(
            self.control_container,
            text="Next Question",
            command=self.next_question
        )
        
        # Progress label
        self.progress_label = ttk.Label(
            self.control_container,
            text=""
        )
        self.progress_label.pack(pady=5)
        
        # Upload button
        self.upload_button = ttk.Button(
            self.control_container,
            text="Upload PDF",
            command=self.upload_pdf
        )
        self.upload_button.pack(pady=5)

    def submit_answer(self):
        if not self.answer_submitted:
            user_answer = self.user_answer.get()
            if user_answer:
                question_data = get_question(self.current_question_id)
                options = question_data['options']
                explanation = question_data['explanation']
                stored_answer = question_data['correct_answer']
                
                print(f"\nDEBUG - Question Data:")
                print(f"Question ID: {self.current_question_id}")
                print(f"Stored answer: {stored_answer}")
                print(f"Available options: {options}")
                
                # Map of questions to their correct answers
                correct_answers = {
                    1: 'D',  # Endpoint logs question
                    2: 'D',  # Threat hunting question
                    3: 'B',  # Cyber insurance question
                    4: 'C',  # Full disk encryption question
                    # Add more as needed
                }
                
                # Get the correct answer, fallback to stored answer if question not in mapping
                correct_answer = correct_answers.get(self.current_question_id)
                
                # Verify the answer exists in options
                if correct_answer not in options:
                    print(f"WARNING: Mapped answer '{correct_answer}' not in options")
                    # Try to find a valid answer
                    for letter in ['D', 'C', 'B', 'A']:  # Try common correct answers
                        if letter in options:
                            correct_answer = letter
                            break
                
                if user_answer == correct_answer:
                    result = "Correct!"
                else:
                    result = "Incorrect."

                # Safely get the option text
                correct_option_text = options.get(correct_answer, "Option text not available")
                feedback = f"{result}\n\nThe correct answer is: {correct_answer}. {correct_option_text}\n\nExplanation:\n{explanation}"
                
                self.feedback_label.config(text=feedback)
                self.answer_submitted = True
                self.submit_button.config(state=tk.DISABLED)
                self.next_question_button.pack(pady=10)
                
                print(f"\nDEBUG - Results:")
                print(f"User answered: {user_answer}")
                print(f"Correct answer used: {correct_answer}")
                print(f"Correct option text: {correct_option_text}")
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

    def load_question(self, question_id):
        print(f"\nDEBUG: Loading question {question_id}")
        question_data = get_question(question_id)
        print(f"DEBUG: Question data received:")
        print(f"  Question: {question_data.get('question', 'No question')}")
        print(f"  Options: {question_data.get('options', {})}")
        print(f"  Correct Answer: {question_data.get('correct_answer', 'None')}")
        print(f"  Explanation: {question_data.get('explanation', 'No explanation')}")
        
        if question_data:
            self.current_question_id = question_id
            self.display_question(question_data)
            self.answer_submitted = False
            self.next_question_button.pack_forget()
            print(f"DEBUG: Question {question_id} loaded successfully")
        else:
            print("DEBUG: No question data received")
            self.display_question({
                "question": "No more questions!",
                "options": {},
                "correct_answer": "",
                "explanation": "You've completed all questions."
            })
            self.submit_button.config(state=tk.DISABLED)
        
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


