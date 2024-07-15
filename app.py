import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import login_required

# Configure application
app = Flask(__name__)
app.config['DEBUG'] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.after_request
def after_request(response):
    # Ensure responses aren"t cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    else:
        provided_id = request.form.get("id").strip()
        provided_password = request.form.get("password").strip()

        # Ensure ID and password were submitted
        if not provided_id and not provided_password:
            flash("Must provide ID and password, error 403")
            return render_template("login.html")

        elif not provided_id:
            flash("Must provide ID, error 403")
            return render_template("login.html")
        
        elif not provided_password:
            flash("Must provide password, error 403")
            return render_template("login.html")

        # Query database for id
        rows = db.execute(
            "SELECT * FROM operators WHERE id = ?", provided_id
        )

        if rows == []:
            flash("ID not found in the database, error 403")
            return render_template("login.html")

        # Ensure password is correct
        if rows[0]['password'] == provided_password:
            # Remember which user has logged in
            session['user_id'] = rows[0]['id']
            # Redirect user to home page
            flash("Login successfully!")
            return redirect('/')
        else:
            flash("Incorrect password, error 403")
            return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Log out successfully!")
    return redirect('/')


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    else:
        # Passing input into variables
        problem_id = request.form.get("problem_id").strip() # ✅
        caller_id = request.form.get("caller_id").strip() # ✅
        operator_id = session['user_id'] # no need for input validation because it's already done in the login process
        reason = request.form.get("reason").strip() # no need for input validation

        # Problem ID validation
        problem_ids = db.execute("SELECT id FROM problems")
        problem_ids_list = []
        for a in problem_ids:
            problem_ids_list.append(a['id'])
        
        try:
            problem_id = int(problem_id)
        except:
            flash("Problem ID must contain only number")
            return render_template("index.html")
        
        if problem_id not in problem_ids_list:
            flash("Problem ID not found")
            return render_template("index.html")

        # Caller ID validation
        caller_ids = db.execute("SELECT id FROM callers")
        caller_ids_list = []
        for i in caller_ids:
            caller_ids_list.append(i['id'])

        try:
            caller_id = int(caller_id)
        except:
            flash("Caller ID must contain only number")
            return render_template("index.html")

        if caller_id not in caller_ids_list:
            flash("Caller ID not found")
            return render_template("index.html")
        
        date = datetime.datetime.now()

        # Logging all the information into the database with the "problems" table as the main part that holds everything together
        db.execute(
            "INSERT INTO calls (caller_id, operator_id, problem_id, reason, date_time) VALUES (?, ?, ?, ?, ?)",
            caller_id,
            operator_id,
            problem_id,
            reason,
            date,
        )

        # Retrieve the last inserted ID
        call_ids = db.execute("SELECT LAST_INSERT_ROWID()")  # Adjust based on your DBMS

        # Assuming problem_id is returned as a list of dictionaries, get the actual ID
        call_id = call_ids[0]['LAST_INSERT_ROWID()']
        print(call_id)
        db.execute(
            "UPDATE calls SET id = ? WHERE date_time = ?", call_id, date
        )

        flash("Follow up call recorded!")
        return render_template("index.html")


@app.route("/search")
def search():
    q = request.args.get("q")
    if q:
        problems = db.execute("SELECT * FROM problems WHERE id LIKE ? LIMIT 5", "%" + q + "%")
    else:
        problems = []
    return render_template("search.html", problems=problems)


@app.route("/create_issue", methods=["GET", "POST"])
@login_required
def create_issues():
    if request.method == "GET":
        return render_template("create_issue.html")
    
    else:
        # Passing input into variables
        caller_id = request.form.get("caller_id").strip() # ✅
        operator_id = session['user_id'] # no need for input validation because it's already done in the login process
        reason = request.form.get("reason").strip() # no need for input validation
        description = request.form.get("description").strip() # no need for input validation
        problem_type = request.form.get("problem_type") # ✅
        serial_number = request.form.get("serial_number").strip() # ✅ bypass a "-"
        product_key = request.form.get("product_key").strip().split(",") # ✅ have to store in a list because the input can be multiple product keys, bypass a "-"

        # Caller ID validation
        caller_ids = db.execute("SELECT id FROM callers")
        caller_ids_list = []
        for i in caller_ids:
            caller_ids_list.append(i['id'])

        try:
            caller_id = int(caller_id)
        except:
            flash("Caller ID must contain only number")
            return render_template("create_issue.html")

        if caller_id not in caller_ids_list:
            flash("Caller ID not found")
            return render_template("create_issue.html")

        # Problem type validation
        if problem_type not in ["os", "software", "hardware"]:
            flash("Invalid problem type")
            return render_template("create_issue.html")
        
        # Serial number validation
        serial_numbers = db.execute("SELECT serial_number FROM devices")
        serial_numbers_list = []
        serial_numbers_list.append("-")
        for j in serial_numbers:
            serial_numbers_list.append(j['serial_number'])

        try:
            serial_number = int(serial_number)
        except:
            if serial_number != "-":
                flash("Serial number must contain only number")
                return render_template("create_issue.html")

        print(serial_number)
        print(serial_numbers_list)
        if str(serial_number) not in serial_numbers_list:
            flash("Device not found")
            return render_template("create_issue.html")
        
        # Product key validation
        product_keys = db.execute("SELECT product_key FROM softwares")
        product_keys_list = []
        product_keys_list.append("-")
        for k in product_keys:
            product_keys_list.append(str(k['product_key']))

        for n in product_key:
            n = n.strip()
            if n not in product_keys_list:
                flash("Software not found")
                return render_template("create_issue.html")

        date = datetime.datetime.now()

        # Logging all the information into the database with the "problems" table as the main part that holds everything together
        # Retrieve problem_type_id
        problem_type_result = db.execute("SELECT id FROM problem_types WHERE problem_type = ?", problem_type)
        print(problem_type_result)

        # Extract the actual problem_type_id
        problem_type_id = problem_type_result[0]['id']
        print(problem_type_id)

        db.execute(
            "INSERT INTO problems (description, problem_type_id, device_serial_number, date_time) VALUES (?, ?, ?, ?)",
            description,
            problem_type_id,
            serial_number,
            date,
        )

        # problem_ids = db.execute("SELECT id FROM problems WHERE description = ?", description)
        # print(problem_ids)

        # Retrieve the last inserted ID
        problem_ids = db.execute("SELECT LAST_INSERT_ROWID()")  # Adjust based on your DBMS

        # Assuming problem_id is returned as a list of dictionaries, get the actual ID
        problem_id = problem_ids[0]['LAST_INSERT_ROWID()']
        print(problem_id)
        db.execute(
            "UPDATE problems SET id = ? WHERE date_time = ?", problem_id, date
        )

        print("product_key", product_key)
        for product in product_key:
            product = product.strip()
            print("product", product)
            print("problem_id", problem_id)
            db.execute(
                "INSERT INTO mapping_problems_softwares (problem_id, software_product_key) VALUES (?, ?)",
                problem_id,
                product,
            )

        db.execute(
            "INSERT INTO calls (caller_id, operator_id, problem_id, reason, date_time) VALUES (?, ?, ?, ?, ?)",
            caller_id,
            operator_id,
            problem_id,
            reason,
            date,
        )

        # Retrieve the last inserted ID
        call_ids = db.execute("SELECT LAST_INSERT_ROWID()")  # Adjust based on your DBMS

        # Assuming problem_id is returned as a list of dictionaries, get the actual ID
        call_id = call_ids[0]['LAST_INSERT_ROWID()']
        print(call_id)
        db.execute(
            "UPDATE calls SET id = ? WHERE date_time = ?", call_id, date
        )

        flash(f"Issue created successfully! Problem ID {problem_id}")
        return render_template("index.html")
    
        # LEFT
        # log info when the user fill the follow up call page
        # write the frontend for the full display page after logging a follow up call
        # write sql to fetch up info onto the full display page

        # write the business proposal
        # write the report
        # record demo video
        # submit the assignment with everything in zip