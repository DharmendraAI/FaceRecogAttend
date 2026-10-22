# Smart Attendance System Using Face Recognition

Python + OpenCV LBPH face recognition + SQLite attendance system for an academic project.

## Features
- Register students and capture face samples using webcam
- Train/update an LBPH recognition model
- Recognize registered students and record attendance
- Prevent duplicate attendance for the same student on the same date
- Print attendance report by date
- SQLite database is created automatically

## Run on Windows
1. Install Python 3.10+ and extract this folder.
2. Open PowerShell in this folder.
3. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Run:
   ```powershell
   python main.py
   ```

## Workflow
1. Choose `1` to register a consenting student and capture face samples.
2. Choose `2` to train the model after registration (repeat after adding students).
3. Choose `3` to start the attendance camera; press Q to stop.
4. Choose `4` for a date-based report.
5. Choose `5` to list students.

## Important
- This is an educational prototype, not a production biometric security system.
- Adjust `THRESHOLD` in `main.py` after testing your own camera and lighting. LBPH confidence values vary.
- There is no liveness detection; photos/screens may fool the prototype. Verify records manually for real use.
- Obtain informed consent before capturing face images. Do not upload real face images, the local database, or trained model to public GitHub.
- The `.gitignore` excludes local biometric data and generated files.

## Files
- `main.py`: application source
- `requirements.txt`: Python dependencies
- `database_schema.sql`: reference schema
- `reports/PROJECT_NOTES.md`: project aim, relationship, test checklist
- `dataset/` and `models/`: empty folders for local data/model files

## GitHub
Create a new repository, e.g. `smart-attendance-face-recognition`, then upload the *contents* of this project folder. Add your name, institute, course and academic year to this README before submission.
