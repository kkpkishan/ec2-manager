# 🖥️ AWS EC2 Instance Manager (Flask + HTML)

A secure web-based dashboard to start/stop AWS EC2 instances. Authenticated users can log in, view instance details, and perform start/stop actions. All actions are logged with user agent, IP, and status details.

---

## 📦 Features

- 🔐 Secure login (credentials stored in `.env`)
- ☁️ List AWS EC2 instances (Name, ID, Type, Status)
- ▶️ Start and ⏹️ Stop instances
- 📑 Logs actions (user IP, user-agent, timestamp, previous status)
- 🌐 View logs in browser
- 🛡️ No database required — flat file (`logs/activity.jsonl`) used for logging

---

## 📁 Project Structure

```

ec2-manager/
│
├── app.py                    # Flask backend
├── .env                      # Username and password
├── Dockerfile                # Docker build file
├── docker-compose.yml        # Docker Compose setup
├── templates/
│   ├── login.html            # Login page
│   ├── dashboard.html        # EC2 control panel
│   └── logs.html             # Logs viewer
├── static/                   # CSS, JS
│   ├── main.css
│   └── main.js
├── logs/
│   └── activity.jsonl        # Log file
└── requirements.txt

````

---

## 🚀 How to Run

### 1. 📥 Clone the repo

```bash
git clone https://github.com/kkpkishan/ec2-manager.git
cd ec2-manager
````

### 2. 🧪 Create `.env` file

Create a `.env` file in the root folder:

```bash
touch .env
```

Add your environment variables:

```
USERNAME=admin
PASSWORD_HASH=your_hashed_password_here
AWS_REGION=ap-south-1
FLASK_SECRET_KEY=your_secret_key
FLASK_DEBUG=1
PORT=5000
```

---

## 🔐 How to Generate a Secure Password Hash

Use Python and Werkzeug to generate a secure password hash:

```python
from werkzeug.security import generate_password_hash

print(generate_password_hash("your_password_here"))
```

Then copy the hash into `.env` as `PASSWORD_HASH`.

---

## 🧪 Run the App (Locally with Python)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## 🐳 Run the App in Docker (Recommended for EC2 with IAM)

### 1. 🏗️ Build the Docker Image

```bash
docker-compose build
```

### 2. 🚀 Run with IAM Role Using `iam-docker-run`

Install [`iam-docker-run`](https://github.com/99designs/iam-docker-run) if not already:

```bash
curl -sSL https://raw.githubusercontent.com/99designs/iam-docker-run/master/install.sh | bash
```

Then start your app:

```bash
iam-docker-run docker-compose up -d
```

> This will ensure the container inherits IAM permissions from the EC2 instance role.

---

## ☁️ IAM Policy to Attach to EC2 Instance Role

To allow EC2 control from the backend running on an EC2 instance, attach this IAM policy to the instance role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 📖 Logging Format

All instance actions are logged to `logs/activity.jsonl` in JSON lines format:

```json
{
  "time": "2025-05-16T13:22:11.923Z",
  "ip": "203.0.113.42",
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
  "instance_id": "i-0abc123def456",
  "action": "stop",
  "previous_status": "running"
}
```

---

## 🖼️ UI Pages

* `/` → Login page
* `/dashboard` → Instance list and actions
* `/logs` → Logs viewer
* `/logout` → End session

---

## 🔐 Security Best Practices

* Use `https://` in production
* Run behind a reverse proxy (e.g., NGINX)
* Secure `.env` and restrict access
* Set file permissions on `logs/` directory
* Rate limit login attempts (optional using Flask-Limiter)

---