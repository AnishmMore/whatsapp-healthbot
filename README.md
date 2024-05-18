# whatsapp-healthbot
## Overview
This project involves creating a WhatsApp bot that can collect basic patient information and export it in a commonly used digital format such as CSV, Google Sheets, or Excel. This solution aims to simplify the process of digitizing health records using widely accessible technology.

## Demo Video
![Demo_video](https://github.com/AnishmMore/whatsapp-healthbot/blob/main/demo_video.mp4)
## Architecture
![Architecture]()
## Libraries Used
- FastAPI
- Uvicorn
- HTTPX
- python-dotenv
- Cryptography
- Passlib[bcrypt]
- python-jose[cryptography]

## Security Audit
### 1. Executive Summary
    Purpose: Assess the security posture of the FastAPI-based application used for collecting and managing patient data via WhatsApp.
    Scope: Covers all components including API, database, WhatsApp bot integration, data storage, and export functionalities.

### 2. Technology Stack
    FastAPI: Used for setting up API endpoints.
    Python-whatsapp-bot: Manages interactions with the WhatsApp Business API.
    SQLite/Other Database/Json: Stores patient data temporarily.
    Cryptography: For data encryption.
    Ngrok: Securely exposes local web server to the internet.
    JWT and RBAC: Manages authentication and role-based access control.

## 3. Threat Model
    Identified Threats:
        Interception of Data: Risk of data being intercepted during transmission.
        Unauthorized Access: Risks associated with inadequate authentication and authorization checks.
        Data Leakage: Potential for sensitive data exposure if encryption keys are mishandled.
    Mitigation Strategies:
        Utilize HTTPS to secure API communication.
        Encrypt sensitive data using Fernet before storing it in the database.
        Implement robust authentication and authorization using JWT and RBAC.

## 4. Security Controls
    Authentication:
        Methods used (JWT tokens).
        Implementation of RBAC for different user roles.
    Authorization:
        Ensuring that users can only access data they are authorized to view.
    Encryption:
        Use of Cryptography's Fernet to encrypt stored data.
        Handling and storage of encryption keys.

## 5. Security Measures Implementation
    Reverse Proxy Using Ngrok: Enforcing HTTPS using ngrok to secure conversations.
    Data Storage and Encryption: Encrypting JSON data using Cryptography's Fernet before storage.
    Authentication and Authorization: Implementing JWT and RBAC to manage access controls.
    Data Export: Securely converting and exporting encrypted data to CSV for authorized users.

This report serves as both an internal document for the development team to address security issues and as a compliance document to reassure stakeholders of the data security measures in place.

## Setup Guide
### Prerequisites
1. Meta Developer Account: Ensure you have a Meta developer account. Create one if needed.
2. Business App: Create a business app in your Meta account. If the option to create a business app is not visible, select "Other > Next > Business".
3. Python Knowledge: Familiarity with Python is required as this tutorial uses Python for the WhatsApp bot.

### Step-by-Step Setup
- Step 1: Set Up Your WhatsApp Environment
  - Add WhatsApp to Your App: Ensure that WhatsApp is added to your Meta business app.
  - API Setup: In your Meta App Dashboard, locate the test number provided for WhatsApp integration. This number will be used to send messages.
  - Verify Your Phone Number: Add and verify your own WhatsApp number in the API setup to send messages.
- Step 2: Send Messages Using the API
  - Access Token: Obtain a 24-hour access token from the API access section of your App Dashboard.
  - Curl Example: Understand the example provided in the dashboard on how to send messages using curl.
  - Python Conversion: Convert the curl command into a Python function using the requests library.
  - Environment Setup: Create a .env file and populate it with necessary variables (e.g., ACCESS_TOKEN, APP_ID) as per the example provided in the dashboard.
  - Send Test Message: Send a "Hello World" message to verify the setup works.
- Step 3: Long-Term Access Token
  - System User: Create a system user in your Meta Business account and assign your WhatsApp app to this user with full control.
  - Generate Token: Generate a new token with extended validity (e.g., 60 days or never expire).
  - Update Environment Variables: Update your .env file with this new long-term access token.
- Step 4: Configure Webhooks to Receive Messages
  - Set Up Local Environment: Ensure your Python environment is ready and all dependencies are installed (pip install -r requirements.txt).
  - Run Local Server: Start your Flask app locally using a script like run.py.
  - Launch Ngrok: Use ngrok to expose your local server to the internet. Follow the steps to set up a static domain.
  - Webhook Configuration: In your Meta App Dashboard, configure the webhook with the ngrok URL and verify it.
- Step 5: Testing and Security
  - Send Test Message: Use the WhatsApp number provided to send a test message to your bot.
  - Receive and Respond: Check if your bot receives and correctly responds to messages.
  - Webhook Security: Implement verification and validation checks as described in the Meta documentation to ensure security.
- Step 6: Build and Expand
  - Learn and Develop: Review the Meta developer documentation to understand more features and capabilities.
  - Expand Functionality: Start building out more features for your WhatsApp bot, such as handling different types of messages or integrating with other services.

## Conclusion
This project provides a scalable and secure way to digitize health records using a WhatsApp bot, leveraging widely accessible technology to improve healthcare delivery and management. The comprehensive guide and robust security measures ensure that patient data is handled with utmost care and confidentiality.


