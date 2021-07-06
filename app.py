from flask import *
from flask import send_from_directory
import psycopg2
import shutil
import imutils
import cv2,pandas as pd
import numpy as np, os, time,pickle
from ParseDocument_v2 import Document
from decode_predictions import decode_predictions
from keras.models import load_model
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
import sys
from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
import argparse
import cv2
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')
from flask_caching import Cache
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
UPLOAD_FOLDER = 'uploads/'
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 100
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/')
def home():
	return render_template('login.html')
@app.route('/result.html')
def download_files():
    return render_template('result.html')
@app.route('/main.html')
def main_page():
    return render_template('main.html')

@app.route('/file')
def download_file():
    file_path = 'D:/OCR-master/Output/Output.txt'
    return send_file(file_path,as_attachment=True,cache_timeout=0)

@app.route('/result2',methods=['GET','POST'])
def gettext():
    if request.method == 'POST':  
        img =request.files['myfile']
        image=img.filename
        print(image)
    counts=0
    global X,Y,W,H
    allOutput = []
    print('==============================================')
    print('Starting ', image)
    print('==============================================') 
    image = cv2.imread(image)
    wd,ht = image.shape[:2]
    img = image.copy()
    obj = Document()
    image, imgCnt = obj.processedImage(image)
    image_with_lines = obj.dilateImage(imgCnt.copy(),150)
    contours = obj.getCountours((image_with_lines.copy()))
    print(type(contours),len(contours))
    contours = obj.sortCountours(contours, "top-to-bottom")
    output = []
    i = 0
    predictedText = []
    for iter, line_Area in enumerate(contours):
        counts = counts + 1
        x,y,w,h = cv2.boundingRect(line_Area)
        X,Y,W,H = x,y,w,h
        line_Image = imgCnt[y:y+h, x:x+w]
        line_Contours = obj.getCountours(imgCnt[y:y+h, x:x+w])
        line_Contours = obj.sortCountours(line_Contours,"left-to-right")
        text = obj.getTextFromImage((image[y:y+h, x:x+w]), line_Contours, Width=8, Height=5)   
        print(text)
        predictedText.append(text)
    print(predictedText)
    while i < len(predictedText):
        x = ' '.join(predictedText[i].split(' ')[1:])
        if len(contours)>9 and i == 2:
        	x = x + ' '.join(predictedText[i+1])
        	i+=1
        output.append(x)
        i+=1
    print('==============================================')
    print('Done with Processing ')
    print('==============================================')
    result=''
    for i in predictedText:
    	result+=i+' '
    allOutput=result
    print(len(allOutput))
    ret = obj.storeData(allOutput)
    if ret == True:
    	print('Done with Scanning.. Result can be found at {}'.format('D:/OCR-master/Output/Output.txt') )
    else:
    	print('Something went wrong while saving the  file..!!!')
    return render_template('result.html')
@app.route('/result1',methods=['GET','POST'])
def tessaract():
	args = {
    
    "east": "D:/OCR-master/frozen_east_text_detection.pb",
    "min_confidence": 0.5,
    "width": 320,
    "height": 320,
    "padding": 0.0
	}
	if request.method == 'POST':  
		img =request.files['myfile1']
		image=img.filename
	image = cv2.imread(image)
	orig = image.copy()
	(origH, origW) = image.shape[:2]
	(newW, newH) = (args["width"], args["height"])
	rW = origW / float(newW)
	rH = origH / float(newH)
	image = cv2.resize(image, (newW, newH))
	(H, W) = image.shape[:2]
	layerNames = [
		"feature_fusion/Conv_7/Sigmoid",
		"feature_fusion/concat_3"]
	print("[INFO] loading EAST text detector...")
	net = cv2.dnn.readNet(args["east"])
	blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
		(123.68, 116.78, 103.94), swapRB=True, crop=False)
	net.setInput(blob)
	(scores, geometry) = net.forward(layerNames)
	(rects, confidences) = decode_predictions(scores, geometry)
	boxes = non_max_suppression(np.array(rects), probs=confidences)
	results = []
	for (startX, startY, endX, endY) in boxes:
		startX = int(startX * rW)
		startY = int(startY * rH)
		endX = int(endX * rW)
		endY = int(endY * rH)
		dX = int((endX - startX) * args["padding"])
		dY = int((endY - startY) * args["padding"])
		startX = max(0, startX - dX)
		startY = max(0, startY - dY)
		endX = min(origW, endX + (dX * 2))
		endY = min(origH, endY + (dY * 2))
		roi = orig[startY:endY, startX:endX]
		config = ("-l eng --oem 1 --psm 7")
		text = pytesseract.image_to_string(roi, config=config)
		results.append(((startX, startY, endX, endY), text))
	results = sorted(results, key=lambda r:r[0][1])
	output=''
	for ((startX, startY, endX, endY), text) in results:
		print("{}\n".format(text))
		text = "".join([c  for c in text]).strip()
		output+=text+' '
	
	obj=Document()
	ret = obj.storeData(output)
	if ret == True:
		print('Done with Scanning.. Result can be found at {}'.format('D:/OCR-master/Output/Output.txt'))
	else:
		print('Something went wrong while saving the  file..!!!')
	return render_template("result.html")


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