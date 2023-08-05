from flask import Flask,render_template,request,redirect,url_for,session

#database connection
import mysql.connector
conn = mysql.connector.connect(host='localhost',user='root',password='',database='BLOODBANK')
mycursor=conn.cursor()
#create a flask application
app = Flask(__name__)

app.secret_key="blood_bank"

#Define the route 
@app.route('/')
def home():
    return render_template('home.html')
#Home menu
@app.route('/home')
def backhome():
    return render_template('home.html')
#Load signup page
@app.route('/donorRegister')
def donorRegister():
    return render_template('donorRegister.html')

#Donor Registration form
@app.route('/donRegister',methods=['POST'])
def donRegister():
    fname=request.form['firstName']
    lname=request.form['lastName']
    dob=request.form['dob']
    bloodGroup=request.form['blood-group']
    lastDonate=request.form['lastDonate']
    phone=request.form['phone']
    city=request.form['city']
    address=request.form['address']
    username=request.form['username']
    password=request.form['password']
    query ="INSERT INTO DONORS(FIRST_NAME,LAST_NAME,DOB,BLOOD_GROUP,LAST_DONATE,PHONE,CITY,ADDRESS,USERNAME,PASSWORD) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data=(fname,lname,dob,bloodGroup,lastDonate,phone,city,address,username,password)
    mycursor.execute(query,data)
    conn.commit()
    return render_template('login.html')

#Login Page
@app.route('/login')
def login():
    return render_template('login.html')

#Check username and password-login process
@app.route('/userHome',methods=['POST'])
def userHome():
    username=request.form['username']
    password=request.form['password']
    if username=='admin':
        query="SELECT * FROM ADMIN WHERE USERNAME = %s AND PASSWORD = %s"
        values=username,password
        mycursor.execute(query,values)
        account=mycursor.fetchall()
        if account:
            query="SELECT COUNT(DONOR_ID) AS DONOR_COUNT FROM DONORS"
            mycursor.execute(query)
            result=mycursor.fetchall()
            query2="SELECT COUNT(DISTINCT BLOOD_GROUP) AS BLOOD FROM DONORS"
            mycursor.execute(query2)
            count=mycursor.fetchall()
            return render_template('adminHome.html',sqldata=result,count=count)
        else:
            msg = 'Incorrect Username or Password!'
        return render_template('login.html',msg=msg)
    else:
        query="SELECT * FROM DONORS WHERE USERNAME = %s AND PASSWORD = %s"
        values=username,password
        mycursor.execute(query,values)
        account=mycursor.fetchone()
        if account:
            session['loggedin']=True
            session['id']=account[0]
            session['name']=account[1]
            return redirect(url_for('donorHome'))
        else:
            msg = 'Incorrect Username or Password!'
        return render_template('login.html',msg=msg)
    
#Load Search Donors Page
@app.route('/search')
def search():
    return render_template('search.html')

#Search Donors and load search result
@app.route('/searchDonors',methods=['POST'])
def searchDonors():
    city=request.form['city']
    bgroup=request.form['blood-group']
    query="SELECT * FROM DONORS WHERE CITY=%s AND BLOOD_GROUP=%s"
    values=city,bgroup
    mycursor.execute(query,values)
    data=mycursor.fetchall()
    if data:
        return render_template('viewDonorsFilter.html',sqldata=data)
    else:
        msg='No Donors!!!'
        return render_template('viewDonorsFilter.html',msg=msg)
        
#Admin part-Dashboard menu
@app.route('/dashboard')
def dashboard():
     query="SELECT COUNT(DONOR_ID) AS DONOR_COUNT FROM DONORS"
     mycursor.execute(query)
     result=mycursor.fetchall()
     query2="SELECT COUNT(DISTINCT BLOOD_GROUP) AS BLOOD FROM DONORS"
     mycursor.execute(query2)
     count=mycursor.fetchall()
     return render_template('adminHome.html',sqldata=result,count=count)

#View Donor List
@app.route('/viewDonors')
def viewDonors():
    query="SELECT * FROM DONORS"
    mycursor.execute(query)
    data=mycursor.fetchall()
    return render_template('viewDonors.html',sqldata=data)

#Delete Donor
@app.route('/deleteDonor/<string:id>')
def deleteDonor(id):
    mycursor.execute("DELETE FROM DONORS WHERE DONOR_ID=%s",(id,))
    conn.commit()
    return redirect(url_for('viewDonors'))
#Admin search donors by city
@app.route('/adminSearchDonors',methods=['POST'])
def adminSearchdonors():
    city=request.form['search']
    mycursor.execute("SELECT * FROM DONORS WHERE CITY=%s",(city,))
    data=mycursor.fetchall()
    return render_template('viewDonors.html',sqldata=data)
#Load Admin change password page
@app.route('/adminSettings')
def adminSettings():
    return render_template('adminSettings.html')

#Admin change password process
@app.route('/adChangePassword',methods=['POST'])
def adChangePassword():
    password=request.form['new']
    confirm=request.form['confirm']
    if password==confirm:
        mycursor.execute("UPDATE ADMIN SET PASSWORD=%s WHERE ADMIN_ID=1",(password,))
        conn.commit()
        msg='Password Updated'
    else:
        msg='Password mismatch..Try again!'
    return render_template('adminSettings.html',msg=msg)

#Donors Part
#Load Donor Home page
@app.route('/donorHome')
def donorHome():
    return render_template('donorHome.html',id=session['id'],name=session['name'])

#Load My account(DonorProfile) page
@app.route('/donorProfile')
def donorProfile():
    id=session['id']
    mycursor.execute("SELECT * FROM DONORS WHERE DONOR_ID=%s",(id,))
    result=mycursor.fetchall()
    return render_template('donorProfile.html',data=result,name=session['name'])

#Donor Update profile
@app.route('/updateProfile',methods=['POST'])
def updateProfile():
    id=request.form['id']
    fname=request.form['firstName']
    lname=request.form['lastName']
    dob=request.form['dob']
    bloodGroup=request.form['blood-group']
    lastDonate=request.form['lastDonate']
    phone=request.form['phone']
    city=request.form['city']
    address=request.form['address']
    mycursor.execute("UPDATE DONORS SET FIRST_NAME=%s,LAST_NAME=%s,DOB=%s,BLOOD_GROUP=%s,LAST_DONATE=%s,PHONE=%s,CITY=%s,ADDRESS=%s WHERE DONOR_ID=%s",(fname,lname,dob,bloodGroup,lastDonate,phone,city,address,id))
    conn.commit()
    mycursor.execute("SELECT * FROM DONORS WHERE DONOR_ID=%s",(id,))
    result=mycursor.fetchall()
    msg='Updated Successfully'
    return render_template('donorProfile.html',data=result,msg=msg,name=session['name'])
#Load donor's Settings page
@app.route('/donorSettings')
def donorSettings():
    id=session['id']
    mycursor.execute("SELECT * FROM DONORS WHERE DONOR_ID=%s",(id,))
    result=mycursor.fetchall()
    return render_template('donorSettings.html',data=result,name=session['name'])

#Donor change password process
@app.route('/donChangePswd',methods=['POST'])
def donChangePswd():
    id=session['id']
    password=request.form['new']
    confirm=request.form['confirm']
    if password==confirm:
        mycursor.execute("UPDATE DONORS SET PASSWORD=%s WHERE DONOR_ID=%s",(password,id))
        conn.commit()
        mycursor.execute("SELECT * FROM DONORS WHERE DONOR_ID=%s",(id,))
        result=mycursor.fetchall()
        msg='Password Updated'
        return render_template('donorSettings.html',data=result,msg=msg,name=session['name'])
    else:
        mycursor.execute("SELECT * FROM DONORS WHERE DONOR_ID=%s",(id,))
        result=mycursor.fetchall()
        msg='Password mismatch..Try again!'
        return render_template('donorSettings.html',data=result,msg=msg,name=session['name'])
    
#donor logout
@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    return redirect(url_for('home'))
 
#Run the flask app
if __name__=='__main__':
    app.run(debug = True)