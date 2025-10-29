
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import PyPDF2
import pickle
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_here'  # Change this in production

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory user store with hashed passwords
users = {
    "admin": {"password": generate_password_hash("Admin@123")}
}

# Store user uploads in memory keyed by username
user_files = {}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Load your trained model (replace with your actual model)
import joblib
model = joblib.load('resume_model.pkl')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def preprocess_text(text):
    # TODO: Add your NLP preprocessing here
    return text

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please fill out all fields.', 'danger')
            return render_template('register.html')

        if username in users:
            flash('Username already exists. Choose a different one.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        users[username] = {'password': hashed_password}
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            user_obj = User(username)
            login_user(user_obj)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            if filename.lower().endswith('.pdf'):
                resume_text = extract_text_from_pdf(filepath)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    resume_text = f.read()

            processed_text = preprocess_text(resume_text)

            # Predict using your model - replace below with actual prediction logic
            # For demo, we return a list of tuples (job role, confidence)
            # e.g. [('Data Scientist', 0.85), ('ML Engineer', 0.75)]
            prediction = [('Data Scientist', 0.85), ('Machine Learning Engineer', 0.75)]

            # Track user's uploaded resumes (in-memory)
            user_files.setdefault(current_user.id, []).append({
                'filename': filename,
                'text': resume_text,
                'prediction': prediction
            })

            return render_template('dashboard.html', prediction=prediction, resume_text=resume_text)
        else:
            flash('Unsupported file format. Use PDF or TXT.', 'danger')
            return redirect(request.url)
    return render_template('dashboard.html')

@app.route('/profile')
@login_required
def profile():
    uploads = user_files.get(current_user.id, [])
    return render_template('profile.html', uploads=uploads)

if __name__ == '__main__':
    app.run(debug=True)