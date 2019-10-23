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
import warnings
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
    warnings.filterwarnings('ignore')
    uname="sharepoint_jade"
    jade_url="https://jade.jhpiego.org/api/categoryOptions?filter=name:like:PRJ&fields=name,id,categoryOptionGroups[name,id,code]&paging=false"

    login=(uname,"Tu!2NQVnRxzhQAmmMt")

    dtable=rq.get(jade_url,auth=login)

    d1=json.loads(dtable.text)

    #Create pd
    df=pd.DataFrame.from_dict(d1, orient='columns')
    df=df['categoryOptions'].apply(pd.Series)
    #Flatten category options groups
    df_p=df['categoryOptionGroups'].apply(pd.Series)
    #df_p.columns=['cat','sec','third']

    #print (df_p)
    df_cat=df_p[0].apply(pd.Series)
    df_cat.rename(columns={'name':'COG_1_name','id':'COG_1_id','code':'COG_1_code'},inplace=True)
    df_cat2=df_p[1].apply(pd.Series)
    df_cat2.rename(columns={'name':'COG_2_name','id':'COG_2_id','code':'COG_2_code'},inplace=True)
    df_cat3=df_p[2].apply(pd.Series)
    df_cat3.rename(columns={'name':'COG_3_name','id':'COG_3_id','code':'COG_3_code'},inplace=True)

    #Combine all
    final_table=pd.concat([df,df_cat,df_cat2,df_cat3],axis=1)
    final_table=final_table.drop(['categoryOptionGroups',0],axis=1)

    final_table['COG.PRJ_name']=np.where(final_table.COG_1_name.str.contains('PRJ'),final_table.COG_1_name,np.where(final_table.COG_2_name.str.contains('PRJ'),final_table.COG_2_name,''))
    final_table['COG.PRJ_id']=np.where(final_table.COG_1_name.str.contains('PRJ'),final_table.COG_1_id,np.where(final_table.COG_2_name.str.contains('PRJ'),final_table.COG_2_id,''))
    final_table['COG.PRJ_code']=np.where(final_table.COG_1_name.str.contains('PRJ'),final_table.COG_1_code,np.where(final_table.COG_2_name.str.contains('PRJ'),final_table.COG_2_code,''))


    final_table['COG.AWD_name']=np.where(final_table.COG_1_name.str.contains('AWD'),final_table.COG_1_name,np.where(final_table.COG_2_name.str.contains('AWD'),final_table.COG_2_name,''))
    final_table['COG.AWD_id']=np.where(final_table.COG_1_name.str.contains('AWD'),final_table.COG_1_id,np.where(final_table.COG_2_name.str.contains('AWD'),final_table.COG_2_id,''))
    final_table['COG.AWD_code']=np.where(final_table.COG_1_name.str.contains('AWD'),final_table.COG_1_code,np.where(final_table.COG_2_name.str.contains('AWD'),final_table.COG_2_code,''))


    final_table=final_table.loc[:,['name','id','COG.PRJ_name','COG.PRJ_id','COG.PRJ_code','COG.AWD_name','COG.AWD_id','COG.AWD_code']]
    final_table.to_csv(os.path.join(app.config['UPLOAD_FOLDER'])+'/data.CSV',index=False)
    return send_from_directory(app.config['UPLOAD_FOLDER'],'data.CSV')



if __name__=='__main__':
   app.debug=True
   app.run()