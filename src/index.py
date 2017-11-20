from flask import Flask, render_template, redirect, url_for, request, g, session, flash
from functools import wraps
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


# To convert the user input password as MD5
def check_password(hashed_password, user_password):
    return hashed_password == hashlib.md5(user_password.encode()).hexdigest()	

# Takes the inputed username and passwords as arguments, and compare them against the users table
def validate(username, password):
    con = sqlite3.connect('var/data.db')
    completion = False
    with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Users")
                rows = cur.fetchall()
                for row in rows:
                    dbUser = row[1]
                    dbPass = row[2]
                    if dbUser == username:
                        completion = check_password(dbPass, password)
    return completion

def init_db():
	with app.app_context():
		con = sqlite3.connect('var/data.db')
		with app.open_resource('var/schema.sql', mode='r') as f:
			con.cursor().executescript(f.read())
		con.commit()
		
def required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        status = session.get('username', False)
        if not status:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorator
	
#The Homepage Route
@app.route("/")
def index():
  return render_template('index.html', title='Home')
  
#The Dashboard Route	
@app.route('/dashboard')
@required
def dashboard():
	con = sqlite3.connect('var/data.db')
	cur = con.execute('SELECT title, day, desc FROM Bucketlist ORDER BY bucket_id desc')
	bucketlist = [dict(title=row[1], day=row[2], desc=row[3]) for row in cur.fetchall()]
	con.close()
	return render_template('dashboard.html', title='Dashboard',  bucketlist=bucketlist)
  
#The Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
#    if request.method == 'POST':
#        username = request.form['username']
#        password = request.form['password']
#        completion = validate(username, password)
#        if completion == False:
#            error = 'Invalid Credentials. Please try again.'
#        else:
#            return redirect(url_for('dashboard'))
#    return render_template('login.html', error=error)

    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
		session['username'] = True
		flash('Welcome! <username>')
        return redirect(url_for('dashboard'))
    return render_template('login.html', error=error, title='Login')

#The Adds to the List
@app.route('/add', methods=['GET','POST'])
def add():
  if not session.get('username'):
      abort(401)
  con = sqlite3.connect('var/data.db')
  con.execute('INSERT INTO Bucketlist (title,day,desc) VALUES(?,?,?)', 
            [request.form['title'], request.form['day'], request.form['desc']])
  con.commit()
  flash('Your Goal Has Been Added To Your List')
  return redirect(url_for('dashboard'))

#The Removes from the List
@app.route('/remove', methods=['GET'])
def remove():
  delete = request.args.get('bucket_id', '')
  print delete
  con = sqlite3.connect('var/data.db')
  con.execute('DELETE FROM Bucketlist WHERE title=?', [delete])
  con.commit()
  cur = con.execute("select * from Bucketlist")
  row = cur.fetchall()
  flash('Your Goal Has Been Removed From Your List')
  return render_template("dashboard.html",row=row)

  
#Logs Out The User from Their Account
@app.route('/logout')
def logout():
  session.pop('username', None)
  flash('You Were Logged Out')
  return redirect(url_for('login'))
	
	
if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
