import os, json
from pathlib import Path
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    session, url_for, flash
)
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, WaiterError

load_dotenv(override=True)

USERNAME      = os.getenv("USERNAME")
PASSWORD_HASH = os.getenv("PASSWORD_HASH")
AWS_REGION    = os.getenv("AWS_REGION", "us-west-2")

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "logs" / "activity.jsonl"
LOG_FILE.parent.mkdir(exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))
ec2 = boto3.client("ec2", region_name=AWS_REGION)

def get_client_ip(req):
    xff = req.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return req.headers.get("X-Real-IP", req.remote_addr)

def log_action(ip, ua, instance_id, action,
               previous_status, current_status,
               success=True, error=""):
    entry = {
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "ip": ip,
        "user_agent": ua,
        "instance_id": instance_id,
        "action": action,
        "previous_status": previous_status,
        "current_status": current_status,
        "success": success,
        "error_message": error,
    }
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(entry) + "\n")

def get_instances():
    instances = []
    for r in ec2.describe_instances()["Reservations"]:
        for inst in r["Instances"]:
            name = next(
                (t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"),
                "N/A"
            )
            instances.append({
                "name":   name,
                "id":     inst["InstanceId"],
                "type":   inst["InstanceType"],
                "status": inst["State"]["Name"],
            })
    return instances

from functools import wraps

def login_required(f):
    @wraps(f)
    def _wrapper(*args, **kw):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kw)
    return _wrapper

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"].strip()
        p = request.form["password"]
        if u == USERNAME and check_password_hash(PASSWORD_HASH, p):
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    instances = get_instances()
    return render_template("dashboard.html",
                           instances=instances,
                           total=len(instances))

@app.route("/action", methods=["POST"])
@login_required
def action():
    instance_id = request.form["instance_id"]
    action      = request.form["action"]

    prev_state = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]["State"]["Name"]

    desired_waiter = {
        "start": ("instance_running", "running"),
        "stop":  ("instance_stopped", "stopped"),
    }

    success, err_msg, current_state = True, "", prev_state
    try:
        if action == "start":
            ec2.start_instances(InstanceIds=[instance_id])
        elif action == "stop":
            ec2.stop_instances(InstanceIds=[instance_id])

        waiter_name, final_state = desired_waiter[action]
        waiter = ec2.get_waiter(waiter_name)
        waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 5, "MaxAttempts": 12})
        current_state = final_state
        flash(f"{instance_id} is now {current_state}", "success")

    except (ClientError, WaiterError) as e:
        success = False
        err_msg = str(e)
        current_state = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]["State"]["Name"]
        flash(f"ERROR: {err_msg}", "danger")

    client_ip = request.form.get("client_ip") or get_client_ip(request)
    log_action(client_ip,
               request.headers.get("User-Agent", "unknown"),
               instance_id, action,
               prev_state, current_state,
               success, err_msg)

    return redirect(url_for("dashboard"))

@app.route("/logs")
@login_required
def view_logs():
    entries = []
    if LOG_FILE.exists():
        with LOG_FILE.open() as f:
            entries = [json.loads(l) for l in f.readlines()][::-1]
    return render_template("logs.html", logs=entries)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0",
            port=port,
            debug=os.getenv("FLASK_DEBUG", "0") == "1")