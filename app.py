from flask import *
app = Flask(__name__)
@app.route('/')
def home():
	return render_template('main.html')
@app.route('/register.html')
def result():
    return render_template('register.html')
@app.route('/login.html')
def results():
    return render_template('login.html')
if __name__ == '__main__':
	app.run(debug=True)