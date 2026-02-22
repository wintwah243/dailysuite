# DailySuite (Smart Daily Management System)

---

## Overview

**DailySuite** is a all-in-one web-based **daily task and productivity management system** built with **Django**.  
It is designed to help users **organize notes, manage tasks, track daily transactions, and interact with the system through a smart assistant interface**.

The system focuses on **simplicity, efficiency, and usability**, providing a clean dashboard, task management feature, budget tracking feature, to-do-list feature and an interactive assistant to improve the daily workflow of users.

DailySuite is built as a **full-stack web application** and serves as both a **university project** and a **practical productivity tool**.

---

## Key Features

- **User Authentication System** — Secure login and user account management plus google login 
- **Task & Daily Activity Management** — Create, update, delete, and track daily tasks  (to-do-list)
- **Command-basd chatbot in Task Management** — chatbot that can perform operations (eg: "add task1 tomorrow", "delete task1", "show pending tasks")
- **Daily Transaction Management** - Create, update, delete, and track incomes & expenses (budget tracking)
- **Command-basd chatbot in Budget Management** — chatbot that can perform operations (eg: "add income salary 5000 today", "show my budget summary", "how much on food?")
- **Note Taking Management** - Create, update, delete, and track users' notes (note taking)
- **Speech-To-Text using Web Speech API** - speech-to-text support for note taking (Language available - Burmese and English)
- **Customer service chatbot** — Interactive assistant to help users inside the system
- **Password Reset via Email** — The system allows users to reset their password through their registered email address using a secure verification process
- **Password Change** — The system enables authenticated users to update their existing password
- **Account Deletion** — The system allows users to permanently delete their account and associated data from the platform

---

## Tech Stack

### **Frontend**
- HTML  
- Tailwind CSS  
- JavaScript  

### **Backend**
- Python (Django Framework)  
- Django Template Engine  
- SQLite
  
### **Development Tools**
- PyCharm  
- Git & GitHub  

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/wintwah243/dailysuite.git
cd dailysuite
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source .venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run the Server
```bash
python manage.py runserver
```

### 7. Open in Browser to see the result
```bash
http://127.0.0.1:8000/
```
---

## Getting started with Docker
#### Make sure you have Docker installed on your system and then open terminal.
### 1. Build the Docker image
```bash
docker build -t dailysuite . 
```

### 2. Run the Docker container
```bash
docker run -p 8000:8000 dailysuite
```

### 3. After that, open your browser and go to:
```bash
http://localhost:8000
```
---

## Team Members

| Name | Role | GitHub Link |
|------|------|---------------|
| **Wint Wah Kyaw Soe** | Leader | https://github.com/wintwah243 |
| **Hsu Wai Linn** | Member | https://github.com/hsuwailinn |
| **Yin Nyein Htwe** | Member | https://github.com/yinnyeinhtwe |
| **Aye Yu Mon** | Member | https://github.com/YuMon9124 |
| **Durga** | Member | https://github.com/Jusiy |

---
