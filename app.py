import os
from flask import Flask, render_template, request, redirect, session, url_for
import boto3
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD_HASH = os.getenv("PASSWORD_HASH")
LOG_FILE = "logs/activity.jsonl"

ec2 = boto3.client('ec2', region_name='us-west-2')

def log_action(ip, user_agent, instance_id, action, prev_state):
    log_data = {
        "time": datetime.utcnow().isoformat(),
        "ip": ip,
        "user_agent": user_agent,
        "instance_id": instance_id,
        "action": action,
        "previous_status": prev_state
    }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_data) + "\n")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form['username'] == USERNAME and
            check_password_hash(PASSWORD_HASH, request.form['password'])):
            session['logged_in'] = True
            return redirect('/dashboard')
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    response = ec2.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'id': instance['InstanceId'],
                'type': instance['InstanceType'],
                'status': instance['State']['Name'],
                'name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            })
    return render_template('dashboard.html', instances=instances)

@app.route('/action', methods=['POST'])
def action():
    if not session.get('logged_in'):
        return redirect('/')
    instance_id = request.form['instance_id']
    action = request.form['action']
    instance_info = ec2.describe_instances(InstanceIds=[instance_id])
    prev_state = instance_info['Reservations'][0]['Instances'][0]['State']['Name']
    if action == 'start':
        ec2.start_instances(InstanceIds=[instance_id])
    elif action == 'stop':
        ec2.stop_instances(InstanceIds=[instance_id])
    log_action(request.remote_addr, request.headers.get('User-Agent'), instance_id, action, prev_state)
    return redirect('/dashboard')

@app.route('/logs')
def view_logs():
    if not session.get('logged_in'):
        return redirect('/')
    with open(LOG_FILE) as f:
        entries = [json.loads(line) for line in f]
    return render_template('logs.html', logs=entries)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
