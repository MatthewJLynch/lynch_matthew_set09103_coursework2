import sqlite3
import os
import sqlite3 as sql

from flask import Flask, g, render_template, url_for, request, redirect, session, escape, flash, abort
from hashlib import md5
from functools import wraps

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
db_location = 'var/wish_db.db'

def required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        status = session.get('username', False)
        if not status:
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorator

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
      db = sqlite3.connect(db_location)
      g.db = db
    return db

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.md5(user_password.encode()).hexdigest()
    print hashed_password

def validate(username, password):
    con = sqlite3.connect(db_location)
    complete = False
    with con:
        cur = con.cursor()

        cur = db.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for row in rows:
            userdb = row[0]
            passdb = row[2]
        if userdb == username:
            complete = check_password(passdb, password)
    return complete

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

#The Sign Up Route	
@app.route('/signup', methods=['GET','POST'])
def signup():
  error = None
  if request.method == 'POST':
    db = get_db()
    cur = db.execute('INSERT INTO users (username,email,password) VALUES(?,?,?)',
                    [request.form['username'], request.form['email'], request.form['password']])
    db.commit()
    return redirect(url_for('dashboard'))
  else:
    error = "Somthing Went Wrong. Try Again!"
    return render_template('signup.html', title='Sign Up')
  return render_template('signin.html', title='Sign Up', error=error)

#The Homepage Route
@app.route("/")
def home():
  return render_template('home.html', title='Home')
  
#The Dashboard Route	
@app.route('/dashboard')
def dashboard():
  #db = get_db()
  #if 'username' in session:
  #   sess = escape(session['username']).capitalize()
  #   return render_template('dashboard.html', session_user=sess, title='Dashboard')
  #return redirect(url_for('dashboard'))

  db = get_db()
  cur = db.execute('select title, quantity, price, details from wishlists order by wish desc')
  wishlists = [dict(title=row[0], quantity=row[1], price=row[2], details=row[3]) for row in cur.fetchall()]
  db.close()
  return render_template('dashboard.html', wishlists=wishlists)

#The Adds a Dream Itam to the List
@app.route('/add', methods=['GET','POST'])
def add():
  if not session.get('username'):
      abort(401)
  db = get_db()
  db.execute('INSERT INTO wishlists (title,quantity,price,details) VALUES(?,?,?,?)', 
            [request.form['title'], request.form['quantity'], request.form['price'], request.form['details']])
  db.commit()
  flash('Your wish has been added to your list')
  return redirect(url_for('dashboard'))

#The Removes a Dream Itam to the List
@app.route('/remove', methods=['GET'])
def remove():
  delete = request.args.get('wishid', '')
  print delete
  db = get_db()
  db.execute('DELETE FROM wishlists WHERE title=?', [delete])
  db.commit()
  cur = db.execute("select * from wishlists")
  row = cur.fetchall()
  flash('Your wish has been removed from your list')
  return render_template("dashboard.html",row=row)

#The About Route
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', songs=songs, title='About')


#The Signs In Route
@app.route('/signin', methods=['GET','POST'])
def signin():
  db = get_db()
  if 'username' in session:
       return redirect(url_for('dashboard'))
  error = None
  if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       complete = validate(username, password)
       if complete == False:
           error = 'Incorrect Username or Password. Please try again.'
       else:
           return redirect(url_for('dashboard'))
       if request.form['username'] != 'admin' or request.form['password'] != 'adminAWT':
           error = 'Incorrect Username or Password, Please try again.'
       else:
           session['username'] = True
           flash('Welcome! You Can Now View Your WounderList')
       return redirect(url_for('dashboard'))
  return render_template('signin.html', error=error, title='Sign In')

#Signs Out The User from Their Account
@app.route('/signout')
def signout():
  session.pop('username', None)
  flash('You Have Successful Signed Out')
  return redirect(url_for('home'))

#Error Page
@app.errorhandler(404)
def page_not_found(error):
  return "We couldn't answer your request. Please try again later or this page might not exist. </br> Please, check your URL", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
