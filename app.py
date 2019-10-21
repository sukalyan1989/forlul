# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 19:27:56 2019

@author: sukalyan
"""
import pandas as pd
import numpy as np
import requests as rq
import json
import getpass
import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory,render_template,send_file

from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.getcwd()+'/Uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',filename=filename))
    filecount=len(os.listdir(os.getcwd()+'/Uploads'))    
    return render_template('upload.html',filecount=filecount)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/lul',methods=['POST'])
def lul():
    uname="sharepoint_jade"
    # print(request.get_json(force=True)['name'])
    jade_url=request.get_json(force=True)['name']
    # jade_url="https://jade.jhpiego.org/api/categoryOptions?filter=name:like:PRJ&fields=name,id,categoryOptionGroups[name,id,code]&paging=false"

    login=(uname,"Tu!2NQVnRxzhQAmmMt")

    dtable=rq.get(jade_url,auth=login)

    d1=json.loads(dtable.text)
    df=pd.DataFrame.from_dict(d1)
    test = df["categoryOptions"].apply(awdprj).apply(pd.Series)
    test.to_csv(os.path.join(app.config['UPLOAD_FOLDER'])+'/data.CSV',index=False)
    return send_from_directory(app.config['UPLOAD_FOLDER'],'data.CSV')




def awdprj(args):
    awd = {}
    prj = {}
    grp = {
        "id": args["id"],
        "name": args["name"]
    }
    if not "categoryOptionGroups" in args:
        return grp
    if len(args["categoryOptionGroups"]) == 0:
        return grp
    if "AWD" in args["categoryOptionGroups"][0]["name"]:
        awd = args["categoryOptionGroups"][0]
        prj = args["categoryOptionGroups"][1]
    else:
        prj = args["categoryOptionGroups"][0]
        awd = args["categoryOptionGroups"][1]
    grp["AWD_id"] = awd["id"]
    grp["AWD_name"] = awd["name"]
    grp["AWD_code"] = awd["code"]
    grp["PRJ_id"] = prj["id"]
    grp["PRJ_name"] = prj["name"]
    return grp


#Create pd

    #Export to CSV


if __name__=='__main__':
   app.debug=True
   app.run()