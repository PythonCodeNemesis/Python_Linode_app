from flask import Flask, request, jsonify
import pymysql
import boto3
import os

app = Flask(__name__)

# Connect to Linode's managed database
conn = pymysql.connect(
    host='http://lin-16251-9474-mysql-primary-private.servers.linodedb.net/',
    user='linroot',
    password=os.environ.get('PASSWORD'),
    db='products'
)

# Connect to Linode's object storage
s3 = boto3.client('s3',
    aws_access_key_id='access_key',
    aws_secret_access_key='secret_key'
)

@app.route('/')
def index():
    return 'Welcome to the Linode Flask App Service!'

@app.route('/store_data', methods=['POST'])
def store_data():
    data = request.get_json()
    cursor = conn.cursor()
    # Store data in Linode's managed database
    sql = "INSERT INTO data (name, email, message) VALUES (%s, %s, %s)"
    cursor.execute(sql, (data['name'], data['email'], data['message']))
    conn.commit()
    # Store relevant photos and documents in Linode's object storage
    if 'photo' in data:
        s3.upload_file(data['photo'], 'bucket_name', 'photo.jpg')
    if 'document' in data:
        s3.upload_file(data['document'], 'bucket_name', 'document.pdf')
    return jsonify({'message': 'Data stored successfully!'})

@app.route('/get_data', methods=['GET'])
def get_data():
    cursor = conn.cursor()
    # Retrieve data from Linode's managed database
    sql = "SELECT * FROM data"
    cursor.execute(sql)
    result = cursor.fetchall()
    data = []
    for row in result:
        data.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'message': row[3]
        })
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run()
