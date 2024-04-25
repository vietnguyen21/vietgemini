from flask import Flask,render_template,request,redirect,url_for,session
from flask_wtf import FlaskForm
from wtforms import TextAreaField,SubmitField
from kernel import generative_text
from flask_sqlalchemy import SQLAlchemy
import bcrypt




app =Flask(__name__)

class take(FlaskForm):
    text = TextAreaField("Request")
    submit = SubmitField("Send Request")

#app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://ufbejk60qp1n4u:p12c9a8306f3c502f8b9231fddc3e02f9b178fb3d1b588a231428b799ba045793@ceu9lmqblp8t3q.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d1tj8nbnvd1pdi'

app.config["SECRET_KEY"] = "mysecret"

db = SQLAlchemy(app)
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(8), nullable=False)
    def __init__(self,password,name):
        self.name = name
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    
    def check_id(self):
        return self.id

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    text = db.Column(db.String(1000),nullable=False)
    question = db.Column(db.String(1000),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    def __init__(self,text,user_id,question):
        self.text = text
        self.question = question
        self.user_id = user_id

    def return_text(self):
        return self.text

    def return_question(self):
        return self.question

@app.route('/home',methods = ["GET","POST"])
def home():
    data = []
    if request.method == "POST":
        data = []
        question_data = []
        present_data = []
        request_text = request.form["question"]
        response = generative_text(str(request_text))

        new_text = History(text=response,question=str(request_text),user_id=user.query.filter_by(name=session['name']).first().check_id())
        db.session.add(new_text)
        db.session.commit()
        history = History.query.filter_by(user_id=user.query.filter_by(name=session['name']).first().check_id()).all()
        for item in history:
            data.append(item.return_text())
            question_data.append(item.return_question())
        for i in range(len(data)):
            data[i] = data[i].replace("*","-")
            data[i] = data[i].split(">")
            for j in data[i]:
                j = j.replace("\n","")
            present_data.append([data[i],question_data[i]])
        present_data.reverse()
        return render_template('index.html',data=present_data)

    return render_template('index.html',data=data)
@app.route('/register',methods=['GET','POST'])
def register():
    check_error = 0
    if request.method == 'POST':
        name = request.form['regname']
        password = request.form['regpass']
        repassword = request.form['reregpass']
        if password == repassword and len(str(password)) >= 8:
            new_user = user(name=name,password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        check_error = 1
        return render_template('register.html',error=check_error)


    return render_template('register.html')

@app.route('/',methods=['GET','POST'])
def login():
    session['name'] = None
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['pass']

        login_user = user.query.filter_by(name=name).first()
        
        if login_user and login_user.check_password(password):
            session['name'] = login_user.name  
            return redirect('/home')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug="True")