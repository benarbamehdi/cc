from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__modele__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'smartphone'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddProduct.html')

@app.route("/addproduct", methods=['POST'])
def AddProduct():
    product_id = request.form['id']
    modele = request.form['modele']
    processeur = request.form['processeur']
    ram = request.form['ram']
    memoire = request.form['memoire']
    batterie = request.form['batterie']
    camera = request.form['camera']
    photo = request.files['photo']

    insert_sql = "INSERT INTO smartphone VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if photo == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (product_id, modele, processeur, ram, memoire, batterie, camera))
        db_conn.commit()
        smartphone_modele = "" + modele + " "
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "product-id-" + str(product_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=photo_in_s3, Body=photo)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                photo_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddProductOutput.html', modele=smartphone_name)


if __modele__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
