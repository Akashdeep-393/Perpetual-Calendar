import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

#Flask
app = Flask(__name__)

#Auto reload
app.config["TEMPLATES_AUTO_RELOAD"] = True

#Disabling caches
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
    
#Configure to filestream
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to SQLite database
db = SQL("sqlite:///calendar.db")

logged_in = False

#Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    
    #Clears existing session
    session.clear()
    
    #When user submits form
    if request.method == "POST":
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        
        #Checks passwords
        if request.form.get("password") != request.form.get("password2"):
             return render_template("apology.html", text ="Passwords must match")
        
        #Checks username
        elif len(rows) != 0:
            return render_template("apology.html", text ="Username already taken")
        
        #Inserts username and password into database
        else:
            password = request.form.get("password")
            hashval = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashval)", username=username, hashval=hashval)
            db.execute("CREATE TABLE :username(Events text, Date date, Day int, Month int, Year int)", username=username)
        
        #months of the year with their lengths
        months = [[1, 31], [2, 28], [3, 31], [4, 30], [5, 31], [6,30], 
                  [7, 31], [8, 31], [9, 30], [10, 31], [11, 30], [12, 31]]
        leap_months = [[1, 31], [2, 29], [3, 31], [4, 30], [5, 31], [6, 30], 
                  [7, 31], [8, 31], [9, 30], [10, 31], [11, 30], [12, 31]]
    
        #loops through the years
        for year in range(2001, 2100):
            
            #loops through the months
            for month in range(1, 13):
                
                #calculates number of days from 1st Jan 2001 to 1st Jan of the current year
                t_year = year - 2001
                beginning_day = (t_year - t_year%4)/4*1461 + t_year%4*365
                days = 0
                
                #calculates number of days from 1st Jan 2001 to the beginning of the current month
                if year%4 != 0:
                    for x in months:
                        if x[0] != month:
                            beginning_day = beginning_day + x[1]
                        if x[0] == month:
                            days=x[1]
                            break
                else:
                    for x in leap_months:
                        if x[0] != month:
                            beginning_day = beginning_day + x[1]
                        if x[0] == month:
                            days=x[1]
                            break
                 
                #calculates number of days from the first new moon of the century to the beginning of the current month
                beginning_moon = beginning_day - 23
                
                #calculates the number of days that have passed since the last newm moon
                beginning_moon = beginning_moon%29.53
            
                #calculates the date of the following new and full moons
                next_new_moon = 0 
                next_full_moon = 0
                if beginning_moon < 15:
                    full_moon = 15 - beginning_moon
                    new_moon = full_moon + 14.53
                    next_full_moon = new_moon + 15
                    if next_full_moon > days:
                        next_full_moon = 0
                    if new_moon > days:
                        new_moon = 0
                    next_full_moon = round(next_full_moon)
                if beginning_moon > 15:
                    new_moon = 29.53 - beginning_moon
                    full_moon = new_moon + 15
                    next_new_moon = full_moon + 14.53
                    if next_new_moon > days:
                        next_new_moon = 0 
                    if full_moon > days:
                        full_moon = 0
                    next_new_moon = round(next_new_moon)
                new_moon = round(new_moon)
                full_moon = round(full_moon)
                if new_moon == 0:
                    new_moon = 1
                if full_moon == 0:
                    full_moon = 1
        
                #converts calculated values to date objects and inserts into database
                newmoon_date = datetime.date(year, month, new_moon)
                fullmoon_date = datetime.date(year, month, full_moon)
                nextnewmoon_date = datetime.date(1, 1, 1)
                nextfullmoon_date = datetime.date(1, 1, 1)
                db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:newmoon, :date, :day, :month, :year)", date=newmoon_date, newmoon="New moon", day=new_moon, month=month, year=year, username=username)
                db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:fullmoon, :date, :day, :month, :year)", date=fullmoon_date, fullmoon="Full moon", day=full_moon, month=month, year=year, username=username)
                if next_new_moon > 0:
                    nextnewmoon_date = datetime.date(year, month, next_new_moon)
                    db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:newmoon, :date, :day, :month, :year)", newmoon="New moon", date=nextnewmoon_date, day=next_new_moon, month=month, year=year, username=username)
                if next_full_moon > 0:
                    nextfullmoon_date = datetime.date(year, month, next_full_moon)
                    db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:fullmoon, :date, :day, :month, :year)", fullmoon="Full moon", date=nextfullmoon_date, day=next_full_moon, month=month, year=year, username=username)
        
                #earliest and latest possible dates for Chinese New Year
                cny1 = datetime.date(year, 1, 20)
                cny2 = datetime.date(year, 2, 18)
            
                #checks if the current new moon is the second new moon after the winter solstice and inserts into database
                if (newmoon_date >= cny1 and newmoon_date < cny2):
                    if new_moon+1 > 31:
                        new_moon = 0
                    cny_date = datetime.date(year, month, new_moon+1)
                    db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:cny, :date, :day, :month, :year)", cny="Chinese New Year", date=cny_date, day=new_moon+1, month=month, year=year, username=username)
                if (nextnewmoon_date >= cny1 and nextnewmoon_date < cny2):
                    if next_new_moon+1 > 31:
                        next_new_moon = 0
                    cny_date = datetime.date(year, month, next_new_moon+1)
                    db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:cny, :date, :day, :month, :year)", cny="Chinese New Year", date=cny_date, day=next_new_moon+1, month=month, year=year, username=username)
                
                #earliest and latest possible dates for Diwali
                diwali1 = datetime.date(year, 10, 21)
                diwali2 = datetime.date(year, 11, 19)
            
                #checks if the current new moon is the second new moon after the autumn equinox and inserts into database
                if (newmoon_date >= diwali1 and newmoon_date < diwali2):
                    db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:diwali, :date, :day, :month, :year)", diwali="Diwali", date=newmoon_date, day=new_moon, month=month, year=year, username=username)
                if (nextnewmoon_date >= diwali1 and nextnewmoon_date < diwali2):
                    db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:diwali, :date, :day, :month, :year)", diwali="Diwali", date=nextnewmoon_date, day=next_new_moon, month=month, year=year, username=username)
            
            #inserts dates for Christmas and New Year into the database    
            christmas_date = datetime.date(year, 12, 25)
            newyear_date = datetime.date(year, 1, 1)
            db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:christmas, :date, :day, :month, :year)", date=christmas_date, christmas="Christmas", day=25, month=12, year=year, username=username)
            db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:newyear, :date, :day, :month, :year)", date=newyear_date, newyear="New Year's Day", day=1, month=1, year=year, username=username)
            
            #calculates number of days since first Eid of the century to the beginning of the current year
            beginning_eid = (t_year - t_year%4)/4*1461 + t_year%4*365
            beginning_eid = beginning_eid - 350
            
            #calculates the number of days since the previous Eid
            beginning_eid = beginning_eid%(29.53*12)
            
            #calculates the number of days until the next Eid
            eidalfitr = 29.53*12 - beginning_eid
        
            #subracts length of each month from above number the date of Eid is obtained and inserted into database
            if year%4 != 0:
                count = 1
                for x in months:
                    if eidalfitr <= x[1]:
                        eidalfitr = round(eidalfitr)
                        eid_date = datetime.date(year, x[0], eidalfitr)
                        db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:eid, :date, :day, :month, :year)",
                        eid="Eid-Al-Fitr", date=eid_date, day=eidalfitr, month=x[0], year=year, username=username)
                        break
                    else:
                        eidalfitr = eidalfitr - x[1]
                        count += 1
            else:   
                count = 1
                for x in leap_months:
                    if eidalfitr <=  x[1]:
                        eidalfitr = round(eidalfitr)
                        eid_date = datetime.date(year, x[0], eidalfitr)
                        db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:eid, :date, :day, :month, :year)",
                        eid="Eid-Al-Fitr", date=eid_date, day=eidalfitr, month=x[0], year=year, username=username)
                        break
                    else:
                        eidalfitr = eidalfitr - x[1]
                        count += 1

        return redirect("/")
    
    #Redirects to registration page   
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])        
def login():
    
    #Clear existing session
    session.clear()
    
    #When user submits form
    if request.method == "POST":
        
        #Verifies username
        if not request.form.get("username"):
            return render_template("apology.html", text = "Must provide username")
        
        #Verifies password
        elif not request.form.get("password"):
             return render_template("apology.html", text = "Must provide password")
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        
        #Verifies username and password
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", text = "Invalid username and/or password. Please register if you have not.")
        
        #Begins new session
        session["user_id"] = rows[0]["id"]
        return redirect("/")
        
    #Redirects to login page
    else:
        return render_template("login.html")
        
@app.route("/", methods=["GET", "POST"])
def index():
    
    #when user submits form
    if request.method == "POST":
        
        #months of the year with their lengths
        months = [[1, 31], [2, 28], [3, 31], [4, 30], [5, 31], [6,30], 
                  [7, 31], [8, 31], [9, 30], [10, 31], [11, 30], [12, 31]]
        leap_months = [[1, 31], [2, 29], [3, 31], [4, 30], [5, 31], [6, 30], 
                  [7, 31], [8, 31], [9, 30], [10, 31], [11, 30], [12, 31]]
     
        #takes user input and calculates the number of days between 1st Jan 2001 and the beginning of the user input month. 
        if session:
            date = datetime.datetime.today()
            if not request.form.get('month'):
                month = date.month
            else:
                month = request.form.get('month')
                month = int(month)
            if not request.form.get('year'):
                year = date.year
            else:
                year = request.form.get('year')
                year = int(year)
            t_year = year - 2001
            beginning_day = (t_year - t_year%4)/4*1461 + t_year%4*365
            days = 0
            if year%4 != 0:
                for x in months:
                    if x[0] != month:
                        beginning_day = beginning_day + x[1]
                    if x[0] == month:
                        days=x[1]
                        break
            else:
                for x in leap_months:
                    if x[0] != month:
                        beginning_day = beginning_day + x[1]
                    if x[0] == month:
                        days=x[1]
                        break
        
            #calculates day of the week on which the month will begin
            beginning_day = beginning_day%7
        
            #outputs month with corresponding events from database
            username = db.execute("SELECT username FROM users WHERE id=:user_id", user_id = session["user_id"])
            events = db.execute("SELECT * FROM :username WHERE Month = :month AND Year=:year", month=month, year=year, username=username[0].get('username'))
            return render_template("indexed.html", year=year, month=month, beginning_day=beginning_day, days=days, events=events)
        
        #redirects user if not logged in
        else:
            return render_template("home.html") 
    
    #when user does not submit form
    else:
        if session:
            return render_template("index.html")
            
        #redirects user if not logged in
        else:
            return render_template("home.html") 

@app.route("/addevent", methods=["GET", "POST"])   
def addevent():
    
    #when user submits form 
    if request.method == "POST":
        if session:
            
            #takes user input event
            if not request.form.get('Event name'):
                return render_template("apology.html", text="Please enter an event")
            elif not request.form.get('Date'):
                return render_template("apology.html", text="Please enter the date")
            elif not request.form.get('Day'):
                return render_template("apology.html", text="Please enter the day")
            elif not request.form.get('Month'):
                return render_template("apology.html", text="Please enter the month")
            elif not request.form.get('Year'):
                return render_template("apology.html", text="Please enter the year")
            else:
                
                #inserts event into database
                username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session["user_id"])
                db.execute("INSERT INTO :username(Events, Date, Day, Month, Year) VALUES (:name, :date, :day, :month, :year)", 
                username=username[0].get('username'), name=request.form.get('Event name'), date=request.form.get('Date'), 
                day=request.form.get('Day'), month=request.form.get('Month'), year=request.form.get('Year'))
            return redirect("/")
        
        #if user is not logged in
        else: 
            return render_template("home.html") 
     
    #when user gets form        
    else:
        if session:
            return render_template("addevent.html")
        
        #if user is not logged in
        else: 
            return render_template("home.html") 
    
    
@app.route("/deleteevent", methods=["GET", "POST"])   
def deleteevent():

    #when user submits form 
    if request.method == "POST":
        if session:
            
            #takes user input event
            if not request.form.get('Event name'):
                return render_template("apology.html", text="Please enter an event")
            elif not request.form.get('Date'):
                return render_template("apology.html", text="Please enter the date")
            
            #inserts event into database
            else:
                Name = request.form.get('Event name')
                Date = request.form.get('Date')
                username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session["user_id"])
                db.execute("DELETE FROM :username WHERE Events = :Name AND Date = :Date", username=username[0].get('username'), Name=Name, Date=Date )
            return redirect("/")
            
        #if user is not logged in    
        else: 
            return render_template("home.html") 
            
    #when user gets form            
    else:
        if session:
            return render_template("deleteevent.html")
        
        #if user is not logged in
        else:
            return render_template("home.html")
            
@app.route("/deleteaccount", methods=["GET", "POST"])
def deleteaccount():
    
    #when user submits form
    if request.method == "POST":
        if session:
            
            #deletes account from database and associated events table
            username = db.execute("SELECT username FROM users WHERE id=:user_id", user_id=session["user_id"])
            db.execute("DELETE FROM users WHERE username = :username", username=username[0].get('username'))
            db.execute("DROP TABLE :username", username=username[0].get('username'))
            session.clear()
            return render_template("home.html") 
            
        #if user is not logged in
        else:
            return render_template("home.html") 
    
    #when user gets form 
    else:
        if session:
            return render_template("deleteaccount.html")
            
        #if user is not logged in
        else: 
            return render_template("home.html")
            
#logout
@app.route("/logout")
def logout():
    
    #clears session
    session.clear()
    
    return redirect("/")
        

                       
            
        
        
        
    

