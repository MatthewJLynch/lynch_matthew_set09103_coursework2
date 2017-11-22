from flask import Flask, render_template, redirect, url_for, request, abort, g, session, flash
from functools import wraps
from hashlib import md5
import sqlite3 as sql
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
db_location = 'var/bucket_list.db'

# Session and redirect to login page 
def required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        status = session.get('username', False)
        if not status:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorator

# Database 
def get_db():
    db = getattr(g, 'db', None)
    if db is None:
      db = sqlite3.connect(db_location)
      g.db = db
    return db

# To convert the user input password as MD5
def check_password(hashed_password, user_password):
    return hashed_password == hashlib.md5(user_password.encode()).hexdigest()
    print hashed_password	

# Takes the inputed username and passwords as arguments, and compare them against the users table
def validate(username, password):
    db = sqlite3.connect(db_location)
    complete = False
    with db:
        cur = db.cursor()

        cur = db.execute("SELECT * FROM Users")
        rows = cur.fetchall()
        for row in rows:
            userdb = row[0]
            passdb = row[2]
        if userdb == username:
            complete = check_password(passdb, password)
    return complete

#init.db - database connection
@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
      db.close()
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('var/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

	
	
#The Homepage Route
@app.route("/")
def index():
  return render_template("index.html", title="Home")
  
#The Dashboard Route	
@app.route("/dashboard")
@required
def dashboard():
	db = get_db()
	cur = db.execute("SELECT title, date, details FROM Bucketlist ORDER BY wish desc")
	bucketlist = [dict(title=row[1], date=row[2], details=row[3]) for row in cur.fetchall()]
	db.close()
	return render_template("dashboard.html", title="Dashboard",  bucketlist=bucketlist)
  
#The Login Route
@app.route("/login/", methods=["GET", "POST"])
def login():
    error = None
#    if request.method == "POST":
#        username = request.form["username"]
#        password = request.form["password"]
#        completion = validate(username, password)
#        if completion == False:
#            error = "Invalid Credentials. Please try again."
#        else:
#            return redirect(url_for("dashboard"))
#    return render_template("login.html", error=error)

    if request.method == "POST":
        if request.form["username"] != "admin" or request.form["password"] != "admin":
            error = "Invalid Credentials. Please try again."
        else:
		session["username"] = True
		flash("Welcome! <username>")
        return redirect(url_for("dashboard"))
    return render_template("login.html", error=error, title="Login")

#The Adds to the List
@app.route("/add", methods=["GET","POST"])
def add():
  if not session.get('username'):
      abort(401)
  db = get_db()
  db.execute("INSERT INTO Bucketlist (title,date,details) VALUES(?,?,?)", 
            [request.form["title"], request.form["date"], request.form["details"]])
  db.commit()
  flash("Your Goal Has Been Added To Your List")
  return redirect(url_for("dashboard"))

#The Removes from the List
@app.route("/remove", methods=["GET"])
def remove():
  delete = request.args.get("wish", "")
  print delete
  db = get_db()
  db.execute("DELETE FROM Bucketlist WHERE title=?", [delete])
  db.commit()
  cur = db.execute("select * from Bucketlist")
  row = cur.fetchall()
  flash("Your Goal Has Been Removed From Your List")
  return render_template("dashboard.html",row=row)

#Sign Up Route
@app.route("/signup", methods=["GET","POST"])
def signup():
  error = None
  if request.method == 'POST':
    db = get_db()
    cur = db.execute('INSERT INTO Users (username,password) VALUES(?,?)',
                    [request.form['username'], request.form['password']])
    db.commit()
    return redirect(url_for('dashboard'))
  else:
    error = "Create A Profile."
    return render_template('signup.html', error=error)
  return render_template('signup.html')
  
#Logs Out The User from Their Account
@app.route("/logout")
def logout():
  session.pop("username", None)
  flash("You Were Logged Out")
  return redirect(url_for("login"))
	
	
if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
