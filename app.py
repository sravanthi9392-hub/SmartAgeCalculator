from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

app.secret_key = "secret123"

# ================= DATABASE ================= #

conn = sqlite3.connect("users.db", check_same_thread=False)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS history(
    username TEXT,
    dob TEXT
)
""")

conn.commit()

# ================= HOME ================= #

@app.route("/")
def home():

    return render_template(

        "index.html",

        page="login",

        username=None

    )

# ================= SIGNUP PAGE ================= #

@app.route("/signup_page")
def signup_page():

    return render_template(

        "index.html",

        page="signup",

        username=None

    )

# ================= SIGNUP ================= #

@app.route("/signup", methods=["POST"])
def signup():

    username = request.form["username"]
    password = request.form["password"]

    cur.execute(

        "SELECT * FROM users WHERE username=?",

        (username,)

    )

    user = cur.fetchone()

    if user:

        return """

        <script>

        alert("User already exists! Please Login.");

        window.location.href="/";

        </script>

        """

    cur.execute(

        "INSERT INTO users VALUES(?,?)",

        (username, password)

    )

    conn.commit()

    return """

    <script>

    alert("Signup Successful! Please Login.");

    window.location.href="/";

    </script>

    """

# ================= LOGIN ================= #

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    # CHECK USER EXISTS

    cur.execute(

        "SELECT * FROM users WHERE username=?",

        (username,)

    )

    existing_user = cur.fetchone()

    if not existing_user:

        return """

        <script>

        alert("User not found! Please Signup First.");

        window.location.href="/signup_page";

        </script>

        """

    # CHECK PASSWORD

    cur.execute(

        "SELECT * FROM users WHERE username=? AND password=?",

        (username, password)

    )

    user = cur.fetchone()

    if not user:

        return """

        <script>

        alert("Incorrect Password! Please Enter Valid Details.");

        window.location.href="/";

        </script>

        """

    session["user"] = username

    return render_template(

        "index.html",

        username=username,

        dashboard=True,

        results=None,

        history=[]

    )

# ================= CALCULATE ================= #

@app.route("/calculate", methods=["POST"])
def calculate():

    if "user" not in session:

        return redirect("/")

    dob = request.form["dob"]

    birth = datetime.strptime(dob, "%Y-%m-%d")

    now = datetime.now()

    diff = now - birth

    years = diff.days // 365
    months = diff.days // 30
    weeks = diff.days // 7
    days = diff.days

    hours = int(diff.total_seconds() // 3600)
    minutes = int(diff.total_seconds() // 60)
    seconds = int(diff.total_seconds())

    results = {

        "Years": years,
        "Months": months,
        "Weeks": weeks,
        "Days": days,
        "Hours": hours,
        "Minutes": minutes,
        "Seconds": seconds

    }

    # NEXT BIRTHDAY

    today = date.today()

    next_birthday = date(today.year, birth.month, birth.day)

    if next_birthday < today:

        next_birthday = date(today.year + 1, birth.month, birth.day)

    remaining = next_birthday - today

    birthday = {

        "days": remaining.days,
        "hours": remaining.days * 24,
        "minutes": remaining.days * 24 * 60

    }

    # SAVE HISTORY

    cur.execute(

        "INSERT INTO history VALUES(?,?)",

        (session["user"], dob)

    )

    conn.commit()

    # FETCH HISTORY

    cur.execute(

        "SELECT dob FROM history WHERE username=? ORDER BY rowid DESC",

        (session["user"],)

    )

    history = cur.fetchall()

    return render_template(

        "index.html",

        username=session["user"],

        dashboard=True,

        results=results,

        birthday=birthday,

        history=history

    )

# ================= LOGOUT ================= #

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")

# ================= RUN ================= #

if __name__ == "__main__":

    app.run(debug=True)