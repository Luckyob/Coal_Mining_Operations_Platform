# ⛏️ MineCore — Coal Mining Operations Platform

> **A smart web-based platform for monitoring, managing, and improving coal mining operations.**
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/fce30db2-829c-42bb-ab0e-072cd6d005a0" />

MineCore provides a centralized platform for monitoring mining sites, tracking production, managing mining stages, monitoring equipment, and maintaining operational safety.

🚀 **Live Demo:**
https://coal-mining-operations-platform.onrender.com/

---

## 🌐 Live Demo

**Try MineCore online:**
👉 https://coal-mining-operations-platform.onrender.com/

Explore the deployed application to see the mining dashboard, production monitoring, mining lifecycle, equipment status, operational alerts, and security tools in action.

---

## 📌 Overview

Coal mining operations involve multiple stages, equipment, sites, safety requirements, and operational decisions. MineCore brings these elements together in one platform.

The system provides a dashboard where users can:

* ⛏️ Monitor the mining lifecycle
* 🏭 Manage multiple mining sites
* 📊 Track production
* 🚜 Monitor equipment
* 🛡️ Monitor operational safety
* 🚨 Review safety and operational alerts
* 🔐 Analyze password security
* 📋 Access mining policy context
* 📱 Use the platform through a responsive web interface

---

## ✨ Key Features

### ⛏️ Mining Operations Dashboard

The main dashboard provides an overview of mining operations, including:

* Today's production
* Active mining sites
* Equipment status
* Open alerts
* Mining lifecycle progress
* Site operational status

### 🏭 Mining Site Management

MineCore supports monitoring multiple mining sites.

Each site provides information such as:

* Site name
* Mining zone
* Current operational stage
* Production
* Site status
* Operational condition
* Equipment
* Alerts

### 🔄 Mining Lifecycle

The platform models the major stages of a mining operation:

1. 🔎 Exploration
2. 📐 Site Planning
3. 🏗️ Mine Development
4. 🚜 Extraction
5. ⚙️ Coal Processing
6. 🚚 Transportation
7. 📦 Storage / Distribution
8. 🌱 Environmental Monitoring & Reclamation

### 🚜 Equipment Monitoring

MineCore provides equipment information associated with mining sites, including operational status and equipment types.

Example equipment includes:

* Excavators
* Haul Trucks

### 🛡️ Safety Monitoring

The platform includes safety-related functionality for mining operations, including:

* Safety checklists
* Safety status
* Operational alerts
* Equipment inspection reminders
* PPE compliance reviews

### 🚨 Operational Alerts

MineCore displays important operational alerts that require attention.

Examples include:

* Equipment inspection reminders
* PPE compliance reviews
* Site safety notifications

### 🔐 Password Security Analyzer

MineCore also includes a standalone password security analyzer.

It evaluates passwords based on security requirements such as:

* Minimum password length
* Uppercase characters
* Lowercase characters
* Numbers
* Special characters
* Extended password length

Passwords receive a strength classification such as:

* 🔴 Weak
* 🟠 Moderate
* 🟢 Strong
* 🔵 Very Strong

  <img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/1d18c3fd-32d2-43a0-afcb-d1e28189624e" />
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/a0494fb9-08df-4eda-8459-f70af1873e7f" />


The analyzer also indicates whether the password satisfies the defined security policy.

### 📚 Policy Context Integration

The platform provides mining-stage policy context through API endpoints designed to support integration with the project's policy explanation functionality.

---

## 🧰 Technology Stack

| Technology    | Purpose                      |
| ------------- | ---------------------------- |
| 🐍 Python     | Backend programming language |
| ⚡ FastAPI     | Web API framework            |
| 🚀 Uvicorn    | ASGI server                  |
| 🌐 HTML       | Web interface                |
| 🎨 CSS        | Interface styling            |
| 📜 JavaScript | Frontend interactivity       |
| ☁️ Render     | Cloud deployment             |
| 🗃️ GitHub    | Source code management       |

---

## 📂 Project Structure

```text
Coal_Mining_Operations_Platform/
│
├── CODE/
│   ├── main.py
│   ├── requirements.txt
│   └── static/
│       └── ...
│
├── README.md
└── ...
```

The main FastAPI application is located in:

```text
CODE/main.py
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Luckyob/Coal_Mining_Operations_Platform.git
```

### 2. Enter the Project Directory

```bash
cd Coal_Mining_Operations_Platform/CODE
```

### 3. Create a Virtual Environment

Windows:

```bash
py -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
py -m uvicorn main:app --reload
```

The application will normally be available at:

```text
http://127.0.0.1:8000
```

---

## 🌐 Main Pages

### 🏠 Main Dashboard

```text
/
```

The main dashboard provides an overview of the mining operation.

### 🏭 Mining Site Dashboard

```text
/sites/{site_id}
```

Displays detailed information for an individual mining site.

---

## 🔌 API Endpoints

### ❤️ Health

```http
GET /health
```

Checks whether the application is running.

### 🔐 Password Security

```http
POST /api/security/password
```

Analyzes password strength and security-policy compliance.

### ⛏️ Mining Stages

```http
GET /api/mining/stages
GET /api/mining/stages/{stage_id}
GET /api/mining/stages/{stage_id}/safety
GET /api/mining/stages/{stage_id}/policy-context
```

Provides mining lifecycle, safety, and policy information.

### 🏭 Mining Sites

```http
GET /api/sites
GET /api/sites/{site_id}
GET /api/sites/{site_id}/equipment
GET /api/sites/{site_id}/alerts
```

Provides mining site, equipment, and alert information.

### 📊 Site Dashboard

```http
GET /api/dashboard/{site_id}
```

Returns consolidated information for a mining site's dashboard.

---

## 📊 Current Demo Data

The deployed demo currently contains multiple mining sites representing different operational conditions.

| Site      | Zone          | Stage           | Status         | Production |
| --------- | ------------- | --------------- | -------------- | ---------: |
| 🏭 Site A | Mining Zone A | Extraction      | Active         | 1,250 tons |
| 🏭 Site B | Mining Zone B | Extraction      | Active         |   980 tons |
| 🏭 Site C | Mining Zone C | Coal Processing | Processing     |   760 tons |
| 🏭 Site D | Mining Zone D | Transportation  | Transportation | 1,120 tons |
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/516f44fe-2060-4c25-bcef-71364afa408e" />

**Total demo production:** 4,110 tons

---

## 🔐 Password Analyzer Criteria

The password analyzer evaluates several security requirements.

| Requirement                     | Score |
| ------------------------------- | ----: |
| Minimum length of 12 characters |    25 |
| Uppercase character             |    15 |
| Lowercase character             |    15 |
| Number                          |    15 |
| Special character               |    15 |
| Length of 16+ characters        |    15 |

### Strength Classification

|    Score | Classification |
| -------: | -------------- |
|   85–100 | 🔵 Very Strong |
|    70–84 | 🟢 Strong      |
|    50–69 | 🟠 Moderate    |
| Below 50 | 🔴 Weak        |

---

## ☁️ Deployment

MineCore is deployed using **Render**.

The production server runs with:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 🌍 Production Application

👉 **https://coal-mining-operations-platform.onrender.com/**

The application is connected to the project's GitHub repository, allowing changes to be deployed through the configured deployment workflow.

---

## 🧪 Testing

Before deploying changes, you can check the Python file for syntax errors:

```bash
py -m py_compile main.py
```

You can then start the application locally:

```bash
py -m uvicorn main:app --reload
```

---

## 📖 API Documentation

The standard FastAPI Swagger UI and ReDoc endpoints are intentionally disabled in the current production configuration.

The application is configured with:

```python
docs_url=None
redoc_url=None
openapi_url=None
```

This means the following endpoints are not publicly exposed:

```text
/docs
/redoc
/openapi.json
```

---

## 🛠️ Development

When developing locally:

1. Create and activate a virtual environment.
2. Install the dependencies.
3. Run the FastAPI application with Uvicorn.
4. Test the dashboard and API endpoints.
5. Check the application for syntax errors before pushing changes.
6. Push changes to GitHub.
7. Verify the deployed version on Render.

---

## 🔒 Security Notes

This project is intended as a hackathon, educational, and demonstration platform.

For a production mining environment, additional security controls would be required, including:

* 🔑 Authentication and authorization
* 👥 Role-based access control
* 🗄️ Persistent database storage
* 🔐 Secure secret management
* 📝 Audit logging
* 🛡️ API security controls
* 🔒 HTTPS configuration and security headers
* 💾 Backup and disaster recovery
* 📊 Production monitoring

The password analyzer is also a demonstration security feature and should not be treated as a complete enterprise password-security system.

---

## 🚧 Project Status

**🟢 Active Development**

MineCore is being developed as a collaborative hackathon project.

Current functionality includes:

* ✅ Mining operations dashboard
* ✅ Mining lifecycle
* ✅ Multiple mining sites
* ✅ Production monitoring
* ✅ Equipment information
* ✅ Safety monitoring
* ✅ Operational alerts
* ✅ Password security analyzer
* ✅ Policy context API
* ✅ Responsive dark interface
* ✅ FastAPI backend
* ✅ Render deployment

Future development can include:

* 🔐 User authentication
* 👤 Role-based access control
* 🗃️ Database integration
* 📈 Historical production analytics
* 📊 Advanced reporting
* 🤖 Expanded AI/policy assistance
* 🔔 Real-time operational notifications
* 📱 Improved mobile experience

---

## 👨‍💻 Author

**Samuel Lucky**


---


## 👥 Collaborators

* [Victor Elias](https://github.com/victorelias471-cloud)
* [Adeemma02](https://github.com/Adeemma02)

## 📜 License

This project is intended for **educational, demonstration, and hackathon purposes**.

---

## ⭐ Explore MineCore

If you want to see the project in action, visit the live deployment:

### 🚀 https://coal-mining-operations-platform.onrender.com/

And explore the source code on GitHub:

### 💻 https://github.com/Luckyob/Coal_Mining_Operations_Platform
