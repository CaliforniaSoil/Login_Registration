from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import md5
import os, binascii
import re

app = Flask(__name__)
mysql = MySQLConnector(app,'registration')
app.secret_key = 'M16b8ink02y2Qki'


@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/processreg', methods=["POST"])
def processreg():
    # get new user data
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    hashed_password = md5.new(request.form['password']).hexdigest()
    #insert data into database
    query = "INSERT INTO registration (first_name, last_name, password, email, created, modified) VALUES (:first_name, :last_name, :password, :email, NOW(), NOW())"
    query_data = {'first_name': first_name, 'last_name': last_name, 'password': hashed_password, 'email': email}
    #check if valid email
    properLogin = True
    my_re = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    check = "SELECT * FROM registration"
    for i in (mysql.query_db(check)):
        if i['email'] == email:
            flash('email aready in database')
            properLogin = False
    if not my_re.match(email):
        flash('please use a proper email')
        properLogin = False
    #check if any fields are blank
    if len(request.form['email']) < 1 or len(request.form['first_name']) < 1 or len(request.form['last_name']) < 1 or len(request.form['password']) < 1 or len(request.form['password']) < 1 or len(request.form['confirm_password']) < 1:
        flash("Please do not leave any blank fields")
        properLogin = False
        return redirect("/")
    #check if first name or last name are too short
    if len(request.form['first_name']) < 2 or len(request.form['last_name']) < 2:
        flash("Names need to be longer than 2 letters")
        properLogin = False
        return redirect("/")
    #check if password is longer than 8 characters
    if len(request.form['password']) < 8:
        flash("Password needs to be longer than 8 characters")
        properLogin = False
        return redirect("/")
    #check if password is entered both times correctly
    if request.form['password'] != request.form['confirm_password']:
        flash("Passwords did not match")
        properLogin = False
        return redirect("/")
    #check if name includes non-alphabetic characters
    if (request.form['first_name']).isalpha() == False or (request.form['last_name']).isalpha() == False:
        flash("Names cannot contain any non-alphabetic characters")
        properLogin = False
        return redirect("/")
    #welcome user to the website
    if properLogin:
        mysql.query_db(query, query_data)
        flash("Welcome to the Jungle {} {}!".format(first_name, last_name))
        return redirect('/success')
    else:
        return redirect('/')

@app.route("/login")
def login():
    session['loggedOn'] = False
    return render_template('login.html')

@app.route("/processlog", methods=["POST"])
def processlog():
    #get user credentials
    email = request.form['email']
    password = request.form['password']
    hashed_password = md5.new(request.form['password']).hexdigest()
    #check if form fields are blank
    if len(request.form['email']) < 1 or len(request.form['password']) < 1 or len(request.form['password']) < 1:
        flash("Please do not leave any blank fields")
        return redirect("/login")

    check = "SELECT * FROM registration"
    #check if the email and password are in the database
    for i in mysql.query_db(check):
        if i['email'] == email and i['password'] == hashed_password:
            session['loggedOn'] = True
            flash('Welcome {} {}!'.format(i['first_name'], i['last_name']))
            return redirect('/success')

    flash('Password or Email Incorrect')
    return redirect('/')
@app.route("/success")
def success():
    return render_template('success.html')


app.run(debug=True)