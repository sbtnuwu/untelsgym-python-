import datetime
import os
import random

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from dotenv import load_dotenv
load_dotenv()

import mysql.connector as myConn
##from flask_session.redis import redis
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'secret_key'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/img/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

plan_fees = {
    'Gym': 750,
    'Gym and Cardio': 1200,
    'Cardio': 700,
    'Zumba': 850,
    'Gym and Zumba': 1500,
    'Gym and Yoga': 1350,
    'Gym and Cardio and Yoga': 1800,
    'Gym and Cardio and Zumba': 2000,
    'Full Access': 2500
}

# Connect to the MySQL database
db = myConn.connect(host="localhost", user="root", password="", database="gym")
db_cursor = db.cursor()
admin_username = 'admin'
admin_password = 'adminpass'


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/classe')
def classe():
    return render_template('class.html')

@app.route('/plans')
def plans():
    return render_template('membership_plans.html')


@app.route('/new_trainer')
def new_trainer():
    return render_template('add_trainer.html')


@app.route('/posts')
def posts():
    # Assuming you have a function to fetch posts from the database
    # Here's a sample query to fetch posts along with the trainer name
    query = """
    SELECT posts.post_id, posts.title, posts.post_description, trainer.name, posts.post_date 
    FROM posts 
    INNER JOIN trainer ON posts.member_id = trainer.trainer_id
    ORDER BY posts.post_date DESC
    """
    db_cursor.execute(query)
    posts_data = db_cursor.fetchall()

    # Assuming each post_data item is a tuple containing (post_id, title, description, trainer_name, post_date)
    posts = []
    for post_data in posts_data:
        post = {
            'post_id': post_data[0],
            'title': post_data[1],
            'description': post_data[2],
            'trainer_name': post_data[3],
            'post_date': post_data[4]
        }
        posts.append(post)

    return render_template('posts.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the provided credentials are for admin login
        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))

        # Query to check if the provided username and password exist in the 'trainer' table
        trainer_query = "SELECT trainer_id FROM trainer WHERE username = %s AND password = %s"
        db_cursor.execute(trainer_query, (username, password))
        trainer_result = db_cursor.fetchone()

        if trainer_result:
            trainer_id = trainer_result[0]
            session['trainer_id'] = trainer_id
            return redirect(url_for('trainer_dashboard'))

        # Query to check if the provided username and password exist in the 'member' table
        member_query = "SELECT member_id FROM member WHERE username = %s AND password = %s"
        db_cursor.execute(member_query, (username, password))
        member_result = db_cursor.fetchone()

        if member_result:
            member_id = member_result[0]
            session['member_id'] = member_id
            return redirect(url_for('member_dashboard'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    # Redirect to the login page or any other desired page after logout
    return redirect(url_for('login'))


@app.route('/upload_meal_plan/<int:member_id>', methods=['POST'])
def upload_meal_plan(member_id):
    if 'admin_logged_in' in session and session['admin_logged_in']:
        if 'meal_plan' in request.files:
            meal_plan = request.files['meal_plan']
            # Save the uploaded file to a folder (e.g., uploads)
            meal_plan.save(os.path.join(app.config['UPLOAD_FOLDER'], meal_plan.filename))
            # Update the member record in the database with the meal plan image filename
            cursor = db.cursor()
            query = "UPDATE member SET meal_plan = %s WHERE member_id = %s"
            cursor.execute(query, (meal_plan.filename, member_id))
            db.commit()
            flash('Meal plan image uploaded successfully!')
        else:
            flash('No meal plan image uploaded.')
        return redirect(url_for('trainer_dashboard'))  # Redirect to trainer dashboard
    else:
        return redirect(url_for('login'))  # Redirect


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        cursor = db.cursor()
        cursor.execute("SELECT trainer_id,name, specialization, contact_number, email,status FROM trainer")
        trainers = cursor.fetchall()
        return render_template('admin_dash.html', trainers=trainers)

    else:
        return redirect(url_for('login'))


@app.route('/add_trainer', methods=['POST'])
def add_trainer():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Insert the data into the 'trainer' table
        query = "INSERT INTO trainer (name, specialization, contact_number, email,username,password) VALUES (%s, %s, " \
                "%s, %s,%s,%s) "
        values = (name, specialization, phone_number, email, username, password)

        try:
            db_cursor.execute(query, values)
            db.commit()
            flash('Trainer added successfully!')

        except Exception as e:
            flash('Error occurred while adding trainer: ' + str(e))

        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard after adding trainer
    else:
        return redirect(url_for('login'))  # Redirect to login page if not logged in as admin


@app.route('/trainer_member/<int:trainer_id>')
def trainer_member(trainer_id):
    if 'admin_logged_in' in session and session['admin_logged_in']:
        cursor = db.cursor()
        query = "SELECT photo, first_name, last_name, email, phone_number, status, member_id FROM member WHERE " \
                "member_id IN (SELECT member_id FROM member_trainer WHERE trainer_id = %s)"
        try:
            cursor.execute(query, (trainer_id,))
            members1 = cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving members: {e}")
            return f"An error occurred: {e}", 500

        # Prepare data for rendering the template
        data = []
        for member in members1:
            member_data = {
                'photo_filename': os.path.basename(member[0]) if member[0] else '',
                'first_name': member[1],
                'last_name': member[2],
                'email': member[3],
                'phone_number': member[4],
                'status': member[5],
                'member_id': member[6]
            }
            data.append(member_data)

        return render_template('trainer_member.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/trainer_dashboard')
def trainer_dashboard():
    db_cursor = db.cursor()

    try:
        db_cursor.execute("""
            SELECT 
                m.first_name, 
                m.last_name, 
                m.email, 
                m.photo, 
                m.status, 
                m.member_id, 
                dp.progress_percentage
            FROM 
                member m
            LEFT JOIN 
                daily_progress dp ON m.member_id = dp.member_id
        """)

        members_with_progress = []
        for row in db_cursor.fetchall():
            member_with_progress = {
                'first_name': row[0],
                'last_name': row[1],
                'email': row[2],
                'photo_filename': row[3],
                'status': row[4],
                'member_id': row[5],
                'progress_percentage': row[6]
            }
            members_with_progress.append(member_with_progress)
    except Exception as e:
        print(f"Error fetching data: {e}")
        members_with_progress = []
    finally:
        db_cursor.close()

    return render_template('trainer_dash.html', members_with_progress=members_with_progress)


@app.route('/member_dashboard')
def member_dashboard():
    # Check if the member is logged in
    if 'member_id' not in session:
        # Redirect to the login page or handle the case where the user is not logged in
        return redirect(url_for('login'))

    # Get the logged-in member's ID from the session
    member_id = session['member_id']

    # Create a cursor object to execute SQL queries
    cursor = db.cursor()

    # Fetch activities for the logged-in member where the activity is assigned (value = 1)
    query_activities = f"SELECT * FROM member_activities WHERE member_id = {member_id} AND \
               (daily_warm_ups = 1 OR marching_spot_jogging = 1 OR wall_push_ups = 1 OR \
               squats = 1 OR mic_chest_press_seated_row = 1 OR mic_leg_press = 1 OR \
               cycle = 1 OR stretch_walk = 1 OR bench_up_down_step = 1 OR \
               db_shoulder_press_triceps_biceps = 1 OR walker = 1 OR kicks = 1 OR \
               crunches_hip_raises = 1 OR cycling_reverse_cycling = 1 OR reverse_curl = 1 OR \
               single_leg_up_down = 1 OR suryanamaskar = 1 OR stretches_shavasana = 1)"

    cursor.execute(query_activities)
    activities_row = cursor.fetchone()  # Assuming only one row per member

    # Convert activities row to dictionary
    activities_dict = {}
    if activities_row:
        activities_dict = {
            'daily_warm_ups': activities_row[1],
            'marching_spot_jogging': activities_row[2],
            'wall_push_ups': activities_row[3],
            'squats': activities_row[4],
            'mic_chest_press_seated_row': activities_row[5],
            'mic_leg_press': activities_row[6],
            'cycle': activities_row[7],
            'stretch_walk': activities_row[8],
            'bench_up_down_step': activities_row[9],
            'db_shoulder_press_triceps_biceps': activities_row[10],
            'walker': activities_row[11],
            'kicks': activities_row[12],
            'crunches_hip_raises': activities_row[13],
            'cycling_reverse_cycling': activities_row[14],
            'reverse_curl': activities_row[15],
            'single_leg_up_down': activities_row[16],
            'suryanamaskar': activities_row[17],
            'stretches_shavasana': activities_row[18]
        }

    # Fetch meal plan filename for the logged-in member
    cursor.execute("SELECT meal_plan FROM member WHERE member_id = %s", (member_id,))
    meal_plan_filename = cursor.fetchone()[0]

    # Fetch trainer information for the logged-in member
    cursor.execute("SELECT t.name, t.specialization, t.contact_number, t.email FROM trainer t \
                    JOIN member_trainer mt ON t.trainer_id = mt.trainer_id \
                    WHERE mt.member_id = %s", (member_id,))
    trainer_info_row = cursor.fetchone()

    # Convert trainer info row to dictionary
    trainer_info = {}
    if trainer_info_row:
        trainer_info = {
            'name': trainer_info_row[0],
            'specialization': trainer_info_row[1],
            'contact_number': trainer_info_row[2],
            'email': trainer_info_row[3]
        }

    # Render the template with activities, meal plan filename, and trainer information
    return render_template('member_dash.html', activities=activities_dict, meal_plan_filename=meal_plan_filename,
                           trainer_info=trainer_info)


from flask import jsonify


@app.route('/insert_progress', methods=['POST'])
def insert_progress():
    if request.method == 'POST':
        progress_percentage = request.form['progress_percentage']
        member_id = session.get('member_id')  # Get member ID from session
        if not member_id:
            return jsonify({'error': 'Member ID not found in session.'}), 400


        db_cursor.execute("SELECT COUNT(*) FROM daily_progress WHERE member_id = %s AND progress_date = CURDATE()",
                          (member_id,))
        count = db_cursor.fetchone()[0]

        if count > 0:

            update_query = "UPDATE daily_progress SET progress_percentage = %s WHERE member_id = %s AND progress_date = CURDATE()"
            values = (progress_percentage, member_id)
            db_cursor.execute(update_query, values)
            db.commit()
            return jsonify({'message': 'Progress updated successfully.'}), 200
        else:

            insert_query = "INSERT INTO daily_progress (member_id, progress_date, progress_percentage) VALUES (%s, CURDATE(), %s) "
            values = (member_id, progress_percentage)
            db_cursor.execute(insert_query, values)
            db.commit()
            return jsonify({'message': 'Progress inserted successfully.'}), 200
    else:
        return jsonify({'error': 'Invalid request method.'}), 400


@app.route('/registration')
def registration():
    return render_template('Registration.html')


@app.route('/workout/<int:member_id>', methods=['GET', 'POST'])
def workout(member_id):
    return render_template('Workout_plan.html', member_id=member_id)


@app.route('/toggle_status/<int:trainer_id>', methods=['POST'])
def toggle_status(trainer_id):
    if 'admin_logged_in' in session and session['admin_logged_in']:
        new_status = request.form.get('status')

        cursor = db.cursor()
        query = "UPDATE trainer SET status = %s WHERE trainer_id = %s"
        cursor.execute(query, (new_status, trainer_id))
        db.commit()
        flash('Trainer status updated successfully!')
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in as admin

@app.route('/member_profile/<int:member_id>')
def member_profile(member_id):
    # Crear un cursor para ejecutar las consultas SQL
    cursor = db.cursor()

    # Consultar la información del miembro
    query_member = """
    SELECT first_name, last_name, phone_number, email, address, height, weight, 
           has_heart_problem, has_hypertension, has_diabetes, has_breathing_problem, 
           has_hernia, has_fracture_dislocation, has_back_pain, has_knee_problem, 
           has_recent_surgery, recent_surgery_details, photo, date_of_birth, gender 
    FROM member WHERE member_id = %s
    """
    cursor.execute(query_member, (member_id,))
    member_info = cursor.fetchone()

    # Cerrar el cursor
    cursor.close()

    if member_info:
        # Preparar los datos del miembro para la plantilla
        member_data = [
            os.path.basename(member_info[16]),  # Foto
            member_info[0],  # Nombre
            member_info[1],  # Apellido
            member_info[2],  # Teléfono
            member_info[3],  # Email
            member_info[4],  # Dirección
            member_info[5],  # Altura
            member_info[6],  # Peso
            member_info[7],  # Problemas del corazón
            member_info[8],  # Hipertensión
            member_info[9],  # Diabetes
            member_info[10],  # Problemas respiratorios
            member_info[11],  # Hernia
            member_info[12],  # Fractura/Dislocaciones
            member_info[13],  # Dolor de espalda
            member_info[14],  # Problemas de rodilla
            member_info[15],  # Cirugía reciente
            member_info[16],  # Detalles de cirugía reciente
            member_info[17],  # Foto (nuevamente para la plantilla)
            member_info[18],  # Fecha de nacimiento
            member_info[19],  # Género
        ]

        # Renderizar la plantilla con los datos del miembro
        return render_template('profile.html', member_data=member_data)
    else:
        # Redirigir a la página de inicio si el miembro no se encuentra
        return redirect(url_for('trainer_dashboard'))

@app.route('/toggle_member_status/<int:member_id>', methods=['POST'])
def toggle_member_status(member_id):
    if 'admin_logged_in' in session and session['admin_logged_in']:
        new_status = request.form.get('status')


        cursor = db.cursor()
        query = "UPDATE member SET status = %s WHERE member_id = %s"
        cursor.execute(query, (new_status, member_id))
        db.commit()

        flash('Member status updated successfully!')
        cursor.execute("SELECT trainer_id FROM member_trainer WHERE member_id = %s", (member_id,))
        trainer_id = cursor.fetchone()[0]  # Assuming trainer_id is the first column

        return redirect(url_for('trainer_member', trainer_id=trainer_id))  # Redirect to admin dashboard
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in as admin

@app.route('/membership', methods=['GET', 'POST'])
def membership():
    if request.method == 'POST':
        username = request.form['username']
        session['username']= username
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        blood_group = request.form['blood_group']

        # Checkboxes for diseases
        has_heart_problem = 'has_heart_problem' in request.form
        has_hypertension = 'has_hypertension' in request.form
        has_diabetes = 'has_diabetes' in request.form
        has_breathing_problem = 'has_breathing_problem' in request.form
        has_hernia = 'has_hernia' in request.form
        has_fracture_dislocation = 'has_fracture_dislocation' in request.form
        has_back_pain = 'has_back_pain' in request.form
        has_knee_problem = 'has_knee_problem' in request.form
        has_recent_surgery = 'has_recent_surgery' in request.form

        recent_surgery_details = request.form['recent_surgery_details']
        height = request.form['height']
        weight = request.form['weight']

        # Convert checkbox values to 1 or 0
        has_heart_problem_value = 1 if has_heart_problem else 0
        has_hypertension_value = 1 if has_hypertension else 0
        has_diabetes_value = 1 if has_diabetes else 0
        has_breathing_problem_value = 1 if has_breathing_problem else 0
        has_hernia_value = 1 if has_hernia else 0
        has_fracture_dislocation_value = 1 if has_fracture_dislocation else 0
        has_back_pain_value = 1 if has_back_pain else 0
        has_knee_problem_value = 1 if has_knee_problem else 0
        has_recent_surgery_value = 1 if has_recent_surgery else 0

        # Insert data into the member table
        query = """
        INSERT INTO member (username, password, first_name, last_name, date_of_birth, gender, email, phone_number, address, 
        blood_group, has_heart_problem, has_hypertension, has_diabetes, has_breathing_problem, has_hernia, 
        has_fracture_dislocation, has_back_pain, has_knee_problem, has_recent_surgery, recent_surgery_details, height, weight)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """
        values = (
            username, password, first_name, last_name, date_of_birth, gender, email, phone_number, address, blood_group,
            has_heart_problem_value, has_hypertension_value, has_diabetes_value, has_breathing_problem_value,
            has_hernia_value,
            has_fracture_dislocation_value, has_back_pain_value, has_knee_problem_value, has_recent_surgery_value,
            recent_surgery_details, height, weight
        )
        db_cursor.execute(query, values)
        db.commit()
    return render_template('membership_plans.html')


@app.route('/select_plan', methods=['GET', 'POST'])
def select_plan():
    if request.method == 'GET':
        selected_plan = request.args.get('title')
        fees = plan_fees.get(selected_plan)
        print(fees)
        db_cursor1 = db.cursor()
        username = session['username']
        query = "SELECT member_id FROM member WHERE username = %s"
        db_cursor1.execute(query, (username,))
        result = db_cursor1.fetchone()  # Fetch the result from db_cursor1, not db_cursor
        if result:
            member_id = result[0]  # Assuming member_id is the first column in the result
            session['member_id'] = member_id

            session['fees'] = fees  # Set the fees in session
            # Store the plan title and member_id in the member_plan table
            query_insert = "INSERT INTO member_plans (member_id, plan_title, fees) VALUES (%s, %s, %s)"
            values = (member_id, selected_plan, fees)
            db_cursor1.execute(query_insert, values)
            db.commit()
    return redirect(url_for('view_profile'))

@app.route('/upload_post', methods=['POST'])
def upload_post():
    if request.method == 'POST':
        trainer_id = session['trainer_id']
        print(trainer_id)
        title = request.form['title']
        post_date = datetime.date.today()
        post_description = request.form['text_description']

        # Insert the post into the posts table
        query = "INSERT INTO posts (member_id, post_description, post_date,title) VALUES (%s, %s,%s,%s)"
        values = (trainer_id, post_description, post_date, title)
        db_cursor.execute(query, values)
        db.commit()

        flash('Post uploaded successfully!')
        return redirect(url_for('trainer_dashboard'))  # Redirect to trainer dashboard after uploading


@app.route('/view_profile')
def view_profile():
    if 'member_id' in session:
        member_id = session['member_id']

        # Fetch user information from the member table
        query_member = "SELECT first_name, last_name, phone_number, email FROM member WHERE member_id = %s"
        db_cursor.execute(query_member, (member_id,))
        member_info = db_cursor.fetchone()

        # Fetch membership plan information from the member_plans table
        query_member_plan = "SELECT plan_title, fees FROM member_plans WHERE member_id = %s"
        db_cursor.execute(query_member_plan, (member_id,))
        member_plan_info = db_cursor.fetchone()

        # Check if both member and membership plan information exist
        if member_info and member_plan_info:
            first_name, last_name, phone_number, email = member_info
            plan_title, fees = member_plan_info
            session['plan_title'] = plan_title;

            # Render the profile template with the fetched information
            return render_template('Payment.html', first_name=first_name, last_name=last_name,
                                   phone_number=phone_number, email=email, plan_title=plan_title, fees=fees)

    else:
        # Handle if member_id is not in the session
        return redirect(url_for('/login'))  # Redirect to login route if session is not available


@app.route('/proceed', methods=['POST'])
def proceed():
    if request.method == 'POST':
        member_id = session.get('member_id')
        transaction_id = request.form['transaction_id']
        payment_date = datetime.date.today()
        fees = session['fees']

        # Insert payment information into the payment table
        query = "INSERT INTO payment (member_id, transaction_id, payment_date, fees) VALUES (%s, %s, %s, %s)"
        values = (member_id, transaction_id, payment_date, fees)
        db_cursor.execute(query, values)
        db.commit()

        plan_title = session['plan_title']
        query = "SELECT trainer_id FROM trainer WHERE specialization = %s"
        db_cursor.execute(query, (plan_title,))
        trainers = db_cursor.fetchall()

        if trainers:
            selected_trainer = random.choice(trainers)
            assignment_date = datetime.date.today()
            member_trainer_query = "INSERT INTO member_trainer (member_id, trainer_id, assignment_date) VALUES (%s, " \
                                   "%s, %s) "
            member_trainer_values = (member_id, selected_trainer[0], assignment_date)
            db_cursor.execute(member_trainer_query, member_trainer_values)
            db.commit()

    if 'photo' in request.files:
        file = request.files['photo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Create the upload folder if it doesn't exist
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            file.save(file_path)

            cursor = db.cursor()
            member_id = session.get('member_id')
            query = "UPDATE member SET photo = %s WHERE member_id = %s"
            values = (file_path, member_id)
            cursor.execute(query, values)
            db.commit()
            flash('File uploaded successfully')

    registration_success = True
    return render_template('login.html', registration_success=registration_success)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/assign_activities', methods=['POST'])
def assign_activities():
    if request.method == 'POST':
        # Get member_id from session or request
        member_id = request.form.get('member_id')

        # Get selected activities from the form
        activities = request.form.getlist('activities[]')

        # Example code to insert activities into the member_activities table
        insert_query = """
        INSERT INTO member_activities 
        (member_id, daily_warm_ups, marching_spot_jogging, wall_push_ups, squats, mic_chest_press_seated_row, 
        mic_leg_press, cycle, stretch_walk, bench_up_down_step, db_shoulder_press_triceps_biceps, walker, kicks, 
        crunches_hip_raises, cycling_reverse_cycling, reverse_curl, single_leg_up_down, suryanamaskar, stretches_shavasana) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Generate parameter values for the placeholders
        values = [member_id] + [str(int(activity in activities)) for activity in [
            'daily_warm_ups', 'marching_spot_jogging', 'wall_push_ups', 'squats', 'mic_chest_press_seated_row',
            'mic_leg_press', 'cycle', 'stretch_walk', 'bench_up_down_step', 'db_shoulder_press_triceps_biceps',
            'walker', 'kicks', 'crunches_hip_raises', 'cycling_reverse_cycling', 'reverse_curl', 'single_leg_up_down',
            'suryanamaskar', 'stretches_shavasana'
        ]]

        # Execute the insert query
        db_cursor.execute(insert_query, values)
        db.commit()

        return redirect(url_for('trainer_dashboard'))  # Redirect to login route if session is not available

    else:
        return "Invalid request method"


@app.route('/profile')
def profile():
    if 'member_id' in session:
        member_id = session['member_id']
        db_cursor = db.cursor()

        # Fetch member information from the member table
        query_member = "SELECT first_name, last_name, phone_number, email, address, height, weight, " \
                       "has_heart_problem, has_hypertension, has_diabetes, has_breathing_problem, " \
                       "has_hernia, has_fracture_dislocation, has_back_pain, has_knee_problem, " \
                       "has_recent_surgery, recent_surgery_details, photo, date_of_birth, gender " \
                       "FROM member WHERE member_id = %s"
        db_cursor.execute(query_member, (member_id,))
        member_info = db_cursor.fetchone()

        # Prepare member data as a list
        member_data = [
            os.path.basename(member_info[16]),  # Photo Filename
            member_info[0],  # First Name
            member_info[1],  # Last Name
            member_info[2],  # Phone Number
            member_info[3],  # Email
            member_info[4],  # Address
            member_info[5],  # Height
            member_info[6],  # Weight
            member_info[7],  # Has Heart Problem
            member_info[8],  # Has Hypertension
            member_info[9],  # Has Diabetes
            member_info[10],  # Has Breathing Problem
            member_info[11],  # Has Hernia
            member_info[12],  # Has Fracture/Dislocation
            member_info[13],  # Has Back Pain
            member_info[14],  # Has Knee Problem
            member_info[15],  # Has Recent Surgery
            member_info[16],  # Recent Surgery Details
            member_info[17],  # Photo
            member_info[18],  # Date of Birth
            member_info[19],  # Gender
        ]

        db_cursor.close()

        # Pass member_data to the HTML template for rendering
        return render_template('profile.html', member_data=member_data)
    else:
        return redirect(url_for('login'))  # Redirect to login page if member_id is not in session


if __name__ == '__main__':
    app.run(debug=True)
