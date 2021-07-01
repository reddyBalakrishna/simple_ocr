from flask import *
import psycopg2
app = Flask(__name__)
@app.route('/')
def home():
	return render_template('main.html')
@app.route('/predict', methods=['GET', 'POST'])
def login():
    msg = ''
    db = psycopg2.connect(
    user="postgres",
    password="Balareddy@8",
    host="localhost",
    port="2548",
    database="OCR")
    if request.method == 'POST' and 'user' in request.form and 'pwd' in request.form:
        username_patient = request.form['user']
        password_patient = request.form['pwd']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM login WHERE username = %s AND password = %s', (username_patient, password_patient,))
        account = cursor.fetchall()
        if account:
            msg = 'Logged in successfully!'
            return render_template('main.html', msg=msg)
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)
@app.route('/results', methods=['GET', 'POST'])
def register():
    msg = ''
    db = psycopg2.connect(
    user="postgres",
    password="Balareddy@8",
    host="localhost",
    port="2548",
    database="OCR")
    if request.method == 'POST':
        username_patient = request.form['user']
        password_patient = request.form['pwd']
        cnfpassword_patient = request.form['cpwd']
        cursor = db.cursor()
        sql = "SELECT * FROM login WHERE username = '%s'" % (username_patient)
        cursor.execute(sql)
        account = cursor.fetchall()
        if account:
            msg = 'Account already exists!'
            return render_template('register.html',msg=msg)
        else:
            insert_query= """ INSERT INTO login (username, password, conformpassword) VALUES (%s,%s,%s)"""
            
            record_to_insert=(username_patient,password_patient,cnfpassword_patient)
            cursor.execute(insert_query,record_to_insert)
            db.commit()
            msg = 'You have successfully registered!'
            return render_template('login.html',msg=msg)
@app.route('/register.html')
def result():
    return render_template('register.html')
@app.route('/login.html')
def results():
    return render_template('login.html')
if __name__ == '__main__':
	app.run(debug=True)
