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
├── templates/
│   ├── login.html            # Login page
│   ├── dashboard.html        # EC2 control panel
│   └── logs.html             # Logs viewer
├── logs/
│   └── activity.jsonl        # Log file
├── static/                   # Optional: CSS, JS
└── requirements.txt

````

---

## 🚀 How to Run

### 1. 📥 Clone the repo

```bash
git clone https://github.com/kkpkishan/ec2-manager.git
cd ec2-manager
````

### 2. 🐍 Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### 4. 🧪 Create `.env` file

Create a `.env` file in the root folder:

```bash
touch .env
```

Add your environment variables:

```
USERNAME=admin
PASSWORD_HASH=your_hashed_password_here
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

## 🧪 Run the App

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

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