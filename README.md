# School Management API built with the use of JWT token authentication.
Built a Simple School Management System API using diffrent libraries and JWT for authentication.

## Features
  - **Admin Functionalities**: Can create and manage other Admins,Student,Teacher,etc.
  - **Teacher Functionalities**: Can arrange/create exams, grade students based on exam answers,etc.
  - **Student Functionalities**: Can update own info,take exam, etc. 
  - **Other Functionalities**: Other Functionalities include Forgot-Change Password,Attendance Management,etc.
    
## Prequisites
  - **Python 3.7.0+**

## Installation

1. **Clone the Repositary:**
```bash
git clone https://github.com/Parth-Bapodara/School-Management-System.git
cd School-Management-System
```
2. **Create Virtual Enviroment:**
```bash
python -m venv venv(Virtual Enviroment Name) # Mac-OS sudo pip install virtualenv
source venv/bin/activate  # Windows: `venv\Scripts\activate' 
```
3. **Install Dependencies:**

   **For Windows or Mac:**
      ```bash
         pip install -r /path/to/requirements.txt
      ```
      ****or****
      ```bash
         python -m pip install -r /path/to/requirements.txt
      ```
   **For Linux:**
     ```bash
        sudo pip install -r requirements.txt
     ```
4. **Run the Application:**
   ```bash
      uvicorn app.main:app --reload
   ```
5. **Access the API:**
   ```bash
      Visit http://<Your Host>/docs for API documentation.
   ```
