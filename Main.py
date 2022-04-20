from flask import Flask, render_template, redirect, url_for, request, session,flash
from flask_sqlalchemy import SQLAlchemy
import random
import os


path = os.path.dirname( os.path.realpath(__file__) )
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+path+'/BankDB.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(80), nullable=False)
	lname = db.Column(db.String(80), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(80), nullable=False)
	sort_code= db.Column(db.String(80), unique=True, nullable=False)
	account_number = db.Column(db.String(80), unique=True, nullable=False)
	balance = db.Column(db.String(8))
    
	def __init__(self, fname, lname, email, password, sc, an, bal):
		self.fname = fname 
		self.lname = lname
		self.password = password
		self.email = email
		self.sort_code = sc 
		self.account_number = an
		self.balance = bal
    	


class Details:
	def accountNum(self):
		return str(random.randint(10000000,99999999)) #return account number as a string
	def sort_code(self):
		num = str(random.randint(120000,129999))
		sc = '12' +'-'+ num[2]+num[3] + '-' +num[4] + num[5] #generate sortcode as a string
		return sc

@app.route('/newUser', methods=['POST','GET'])
def newUser():
	print(request.method)
	if request.method == 'POST':
		session.permanent = True  #create permanent session

		first_name = request.form['firstName'] #get details from html form 
		last_name = request.form['LastName']
		email = request.form['email']
		password = request.form['password']


		found_email = User.query.filter_by(email = email).first() #check if user already exists

		if first_name != '' and last_name != '' and email != '' and password != '':
			if found_email:
				flash('email already in use')
				return render_template('SignUp.html')
			elif len(password) < 6:
				flash('Password must be at least 6 characters long')
				return render_template('SignUp.html')
			else:
				details = Details()  #create instance of details class
				sortCode = details.sort_code() #generate sort code
				accNo = details.accountNum() # generate account number
				session['sortcode'] = sortCode
				session['accountNum'] = accNo
				bal = 50

				session['user'] = first_name
				session['lname'] = last_name

				newUser = User(first_name, last_name, email, password, sortCode,accNo, bal)
				db.session.add(newUser)
				db.session.commit()
				return(redirect(url_for('home')))
		else:
			flash('Details cannot be left blank')
			return render_template('SignUp.html')
	else:
		return render_template('SignUp.html')


@app.route('/login', methods=['POST','GET'])
def login():
	if request.method == 'POST':
		email = request.form['email'] #get email input value
		password = request.form['password'] #get password input value
		

		if type(email) == None or type(password) == None: #check that there is a non empty input
			user = User.query.filter_by(email = email).first() #get user details from database
			if password == user.password and email == user.email: #if user exists, check if email AND password entered match those in the db.				
				session['user'] = user.fname #set session user
				#session['balance'] = user.balance #get user balance (remove this and call balance directly from database when needed)
				session['sortcode'] = user.sort_code #get user's sort code
				session['accountNum'] = user.account_number #get user account number
				return(redirect(url_for('home')))
			
			else: 	
				flash('Incorrect username or password') #if email and password do not match, flash message 
				return render_template('Login.html')
		else:
			return render_template('Login.html')
	else:
		return render_template('Login.html')


@app.route('/home')

def home():
	if 'user' in session:
		user = User.query.filter_by(fname= session['user']).first()
		return render_template('Home.html', usr= session['user'], balance = str(user.balance), sortcode=user.sort_code, accno=user.account_number)
	else:
		return redirect(url_for('login'))


@app.route('/moveMoney', methods=['POST','GET'])
def moveMoney():
	if 'user' in session:

		sender = User.query.filter_by(sort_code = session['sortcode'], account_number = session['accountNum']).first()

		if request.method == 'POST':
			recipientName = request.form['toName']
			sortCode = request.form['toSC']
			accNo = request.form['toAN']
			amount = request.form['amount']
			recipient = User.query.filter_by(sort_code = sortCode, account_number = accNo).first()

			if recipient != None and recipientName == recipient.fname + ' ' + recipient.lname:	#check if details are valid
				strRecBal = float(recipient.balance) #gets balance of recipient
				strRecBal += float(amount) # adds the transferred amount to balance
				strSenBal = float(sender.balance) #gets senders balance
				strSenBal -= float(amount) # subtracts transferred amount from balance
				
				recipient.balance = strRecBal #updates recipient balance
				sender.balance = strSenBal #updates senders balance
				db.session.commit() #commits updates to database

				return redirect(url_for('home')) #redirect to home
			else:
				flash('Account not found')
				return render_template('Transfer.html', sc = sender.sort_code, an = sender.account_number)
		else:
			return render_template('Transfer.html', sc = sender.sort_code, an = sender.account_number)
	else:
		return redirect(url_for('login'))



@app.route('/logout')
def logout():
	session.clear()
	return(redirect(url_for('login')))



if __name__ == "__main__":
	db.create_all()
	app.run(debug = True)