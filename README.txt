========================================
   DENTAL CLINIC MANAGEMENT SYSTEM
========================================

Version: 1.0
Date: April 2025

========================================
   SYSTEM REQUIREMENTS
========================================

- Windows 10 or Windows 11
- 4GB RAM minimum
- 100MB free disk space
- Google Chrome (recommended) or any modern browser
- Internet connection (only for first time setup)

========================================
   INSTALLATION STEPS
========================================

1. Copy the entire folder to your computer
   (Recommended location: C:\DentalClinic)

2. Open the folder

3. Double-click "start_dental_clinic.bat"

4. Wait for "SERVER IS RUNNING!" message

5. Open Google Chrome

6. Type this address: http://127.0.0.1:5000

7. Press Enter

========================================
   HOW TO USE THE SYSTEM
========================================

--- ADD A NEW PATIENT ---
1. Click "Add Patient" button
2. Enter patient name, phone number, email
3. Click "Save Patient"

--- CHECK IN A PATIENT ---
1. Click "Patients" in menu
2. Find the patient
3. Click "Check In" button
4. Enter Slip Fee (upfront payment)
5. Click "Confirm Check In"

--- ADD PROCEDURES & PAYMENTS ---
1. After check-in, you're on the Visit page
2. Fill the "Add Procedure" form:
   - Procedure name (e.g., "Cleaning", "Filling")
   - Procedure cost
   - Amount paid by patient
   - Any notes
3. Click "Add Procedure"

--- PRINT A SLIP ---
1. On the Visit page
2. Click "Print Slip" button
3. Click "Print" in the new window
4. Close the print window

--- VIEW PATIENT HISTORY ---
1. Click "Patients" in menu
2. Click "View" next to any patient
3. See all previous visits and procedures

--- EDIT PATIENT INFO ---
1. Click "Patients" in menu
2. Click "Edit" next to any patient
3. Update information
4. Click "Save Changes"

--- DELETE A PATIENT ---
1. Click "Patients" in menu
2. Click "Delete" next to any patient
3. Confirm deletion (this removes ALL records)

--- VIEW REPORTS ---
1. Click "Reports" in menu
2. Select time period (7, 30, 90, 365 days)
3. View:
   - Total revenue
   - Number of visits
   - Average per visit
   - Daily breakdown
   - All visit details

========================================
   STOPPING THE SYSTEM
========================================

- Click anywhere in the black Command Prompt window
- Press any key
- The system will shut down

OR

- Simply close the black Command Prompt window

========================================
   BACKUP YOUR DATA
========================================

Your data is stored in "clinic.db" file.

TO BACKUP:
1. Close the system
2. Copy "clinic.db" to a USB drive or cloud storage

TO RESTORE:
1. Close the system
2. Copy your backup file to the folder
3. Replace the existing "clinic.db"
4. Restart the system

========================================
   TROUBLESHOOTING
========================================

PROBLEM: Page doesn't open (http://127.0.0.1:5000)

SOLUTION:
- Make sure the black Command Prompt window is OPEN
- If closed, double-click "start_dental_clinic.bat" again
- Wait 5 seconds after "SERVER IS RUNNING!" message
- Refresh the browser page

PROBLEM: "Python is not recognized"

SOLUTION:
- Python is not installed on this computer
- Download from: https://python.org/downloads/
- Install Python (check "Add to PATH")
- Restart the system

PROBLEM: System is slow

SOLUTION:
- Close other programs
- Restart the system
- Check if computer has enough RAM

PROBLEM: Can't find a patient

SOLUTION:
- Use the search bar on Patients page
- Type name, phone number, or email
- The list filters automatically

========================================
   FEATURES COMING SOON
========================================

- WhatsApp messages to patients
- Appointment reminders
- Multiple clinic locations
- Cloud backup
- Monthly subscription option

========================================
   SUPPORT
========================================

For support, contact:
[Shaheer Zia]
[+923029169919]
[shaheerzia6@gmail.com]

========================================
   THANK YOU FOR CHOOSING OUR SYSTEM!
========================================