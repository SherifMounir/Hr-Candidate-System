from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Job , UserData
from . import db
import json
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField ,StringField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired ,DataRequired ,Length
from pyresparser import ResumeParser
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
# from lxml.html import fromstring

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        job = request.form.get('job')
        skills = request.form.get('skills') 


        if len(job) < 1 and len(skills) < 1 :
            flash('job is not completed!', category='error') 
        else:
            new_job = Job(title=job, Required_skills=skills , user_id=current_user.id)  #providing the schema for the job 
            db.session.add(new_job) #adding the note to the database 
            db.session.commit()
            flash('Job added!', category='success')
    hr_users = User.query.filter_by(category='hr').all()
    return render_template("home.html", user=current_user , hrs = hr_users)


@views.route('/delete-job', methods=['POST'])
def delete_job():  
    job = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    jobId = job['job_Id']
    job = Job.query.get(jobId)
    if job:
        if job.user_id == current_user.id:
            for candidate in job.candidates:
                db.session.delete(candidate)
                db.session.commit()
            db.session.delete(job)
            db.session.commit()
    hr_user = User.query.filter_by(email='hr@gmail.com').first()
    return render_template("home.html", user=current_user , hr=hr_user)


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    job_id = StringField('job_id',validators=[DataRequired(), Length( min=1, max=20)])
    submit = SubmitField("APPLY")  

def logisticRegressionModel(data):
    df = pd.read_csv(os.path.join(os.path.abspath(os.path.dirname(__file__)),'static/CVs','training_dataset.csv'))
    df = df.replace(['Female'], 0)
    df = df.replace(['Male'], 1)
    df = df.replace(['extraverted'], 1)
    df = df.replace(['serious'], 2)
    df = df.replace(['dependable'], 3)
    df = df.replace(['lively'], 4)
    df = df.replace(['responsible'], 5)
    presonalityDes = {1: 'extraverted',
                      2: 'serious',
                      3: 'dependable',
                      4: 'lively',
                      5: 'responsible'
                      }
    X = df.iloc[:, :-1].values
    Y = df.iloc[:, -1].values
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20, random_state=2)
    reg = LogisticRegression(solver='lbfgs')
    reg.fit(X_train, Y_train)
    newUser = np.array(data, dtype=float).reshape(1, -1)
    presonality_pred = reg.predict(newUser)[0]
    return presonalityDes[presonality_pred]    

def createBagOfWord(userResumeData , jobRequiredSkills):
    bagOfWord = []
    for skill in userResumeData['skills']:
        skills = skill.split(' ')
        for item in skills:
            bagOfWord.append(item)
    # uniqueWords = set(bagOfWord).union(set(bagOfWordsB))
    uniqueWords = set(bagOfWord)
    numOfBOW = dict.fromkeys(uniqueWords, 0)
    for jobskill in jobRequiredSkills:
        if jobskill in numOfBOW.keys():
            numOfBOW[jobskill] += 1
    return numOfBOW

def computeTF(wordDict, bagOfWords):
    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict

def computeIDF(documents):
    import math
    N = len(documents)

    idfDict = dict.fromkeys(documents[0].keys(), 0)
    for document in documents:
        for word, val in document.items():
            if val > 0:
                idfDict[word] += 1

    for word, val in idfDict.items():
        idfDict[word] = math.log(N / float(val+1))
    return idfDict

def computeTFIDF(tfBagOfWords, idfs):
    tfidf = {}
    for word, val in tfBagOfWords.items():
        tfidf[word] = val * idfs[word]
    return tfidf

@views.route('/apply', methods=['GET','POST'])
def apply_for_job():
    # spinner = '<div id="spinner" class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>'
    # parsed_html = fromstring(spinner)
    # element = parsed_html.get_element_by_id("spinner")
    # if element.style.display == "none":
    #      element.style.display = "block";
  
    form = UploadFileForm()
    hr_user = User.query.filter_by(email='hr@gmail.com').first()
    ds_keyword = ['tensorflow', 'keras', 'pytorch', 'Programming', 'machine learning', 'deep Learning',
                                  'flask', 'streamlit', 'Matlab', 'Research', 'learning', 'Analysis', 'Mining', 'Data']
    web_keyword = ['Illustrator', 'react', 'django', 'Programming', 'node jS', 'react js', 'php',
                                   'Analysis', 'laravel', 'magento', 'wordpress',
                                   'javascript', 'angular js', 'c#', 'flask', 'Programming']
    android_keyword = ['Strategy', 'Design', 'Adobe', 'Interactive', 'Photoshop', 'Prototyping',
                                       'Programming', 'Indesign', 'Analysis', 'android', 'android development',
                                       'flutter', 'kotlin', 'xml', 'kivy']
    ios_keyword = ['International', 'Communication', 'Programming', 'Architecture', 'Rest', 'ios',
                                   'ios development', 'swift', 'cocoa', 'cocoa touch', 'Analysis', 'xcode']
    uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                    'Programming', 'storyframes', 'adobe photoshop', 'photoshop', 'editing',
                                    'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects',
                                    'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe',
                                    'solid', 'grasp', 'user research', 'user experience']
    if request.method == 'POST':
        if form.validate_on_submit():
            file = form.file.data # First grab the file
            print("submit data :" ,form.submit)
            jobId = form.job_id.data
            job = Job.query.get(jobId)
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),'static/CVs',secure_filename(file.filename))) # Then save the file
            flash('File has been uploaded.', category='success')
            # jobId = request.form.get('jobId')
            # job = Job.query.get(jobId)
            requiredSkills = job.Required_skills.split(", ")
            userResumeData = ResumeParser(os.path.join(os.path.abspath(os.path.dirname(__file__)),'static/CVs',secure_filename(file.filename))).get_extracted_data()
            numOfBOW_web = createBagOfWord(userResumeData, web_keyword)
            numOfBOW_and = createBagOfWord(userResumeData, android_keyword)
            numOfBOW_ios = createBagOfWord(userResumeData, ios_keyword)
            numOfBOW_ui  = createBagOfWord(userResumeData, uiux_keyword)
            if userResumeData:
                numOfBOW_ds = createBagOfWord(userResumeData, requiredSkills)
                tfA = computeTF(numOfBOW_ds, requiredSkills)
                idfs = computeIDF([numOfBOW_ds, numOfBOW_web, numOfBOW_and, numOfBOW_ios, numOfBOW_ui])
                tfidfA = computeTFIDF(tfA, idfs)
                resumescore = 0
                print("TFFFFF : ", tfidfA)

                for word, value in tfidfA.items():
                    resumescore += value * 5
                
                if resumescore == 0:
                    resumescore += 30
                else:
                    resumescore += 50

                level = 'Entry level'
                if resumescore >= 50:
                    level = 'Intermedite'   
                candidate_data = UserData(Name=userResumeData['name'] , 
                                          email=userResumeData['email'],
                                          resume_score=str(int(resumescore)),
                                          Page_no=str(userResumeData['no_of_pages']),
                                          Predicted_Field='NOT YET',
                                          User_level=level,
                                          Actual_skills=str(userResumeData['skills']),
                                          user_id=current_user.id,
                                          job_id=job.id)
                db.session.add(candidate_data)
                db.session.commit()
                flash('Your CV Score For This Job is : '+ str(int(resumescore)) , category='success')
                hr_users = User.query.filter_by(category='hr').all() 
                return render_template("home.html", user=current_user , hrs=hr_users, hr=hr_user  , form=form)
    hr_users = User.query.filter_by(category='hr').all()
    return render_template("apply.html", user=current_user , hrs=hr_users, hr=hr_user , form=form)

@views.route('/personalityTest', methods=['GET','POST'])
def personalityTest():
     if request.method == 'POST':
            gender = request.form.get('options')
            age = request.form.get('age')
            openness = request.form.get('openness') 
            neuroticism = request.form.get('neuroticism') 
            conscientiousness = request.form.get('conscientiousness') 
            agreeableness = request.form.get('agreeableness') 
            extraversion = request.form.get('extraversion') 
            if len(age) < 1  :
                flash('Age is not Entered!', category='error') 
            else:
                if gender == 'male':
                    gender = 1
                elif gender == 'female':
                    gender = 0
                personalityPrediction = logisticRegressionModel([gender,age,openness,neuroticism,conscientiousness,agreeableness,extraversion])   
                applicants = UserData.query.filter_by(user_id=current_user.id).all()
                if applicants:
                    for applicant in applicants:
                        applicant.Predicted_Field = str(personalityPrediction)
                        db.session.commit()
                    flash('Your Personality is  '+ str(personalityPrediction) , category='success') 
                    flash('Your Personality Test Evaluation Saved With your CV Data.  ' , category='success') 
                else:
                    flash('Your MUST Apply For a Job And Upload your CV First!  ' , category='error') 
    


             
     hr_user = User.query.filter_by(email='hr@gmail.com').first()
     return render_template("personalityTest.html", user=current_user , hr=hr_user) 
