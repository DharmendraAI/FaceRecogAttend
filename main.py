import os
import sqlite3
from datetime import datetime, date
import cv2
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "attendance.db")
DATASET = os.path.join(BASE, "dataset")
MODEL = os.path.join(BASE, "models", "lbph.yml")
SIZE = (200, 200)
SAMPLES = 40
THRESHOLD = 65.0  # LBPH distance: lower is a closer match.

def connect():
    return sqlite3.connect(DB)

def setup():
    os.makedirs(DATASET, exist_ok=True)
    os.makedirs(os.path.join(BASE, "models"), exist_ok=True)
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS students(
            student_id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            department TEXT NOT NULL, created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS attendance(
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL, attendance_date TEXT NOT NULL,
            attendance_time TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            UNIQUE(student_id, attendance_date))""")

def detector():
    d = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if d.empty():
        raise RuntimeError("Could not load OpenCV face detector.")
    return d

def register():
    try:
        sid = int(input("Unique numeric student ID: ").strip())
    except ValueError:
        print("ID must be numeric."); return
    name = input("Student name: ").strip()
    dept = input("Department/class: ").strip()
    if not name or not dept:
        print("Name and department are required."); return
    with connect() as c:
        if c.execute("SELECT 1 FROM students WHERE student_id=?", (sid,)).fetchone():
            print("That ID already exists."); return
        c.execute("INSERT INTO students VALUES(?,?,?,?)",
                  (sid, name, dept, datetime.now().isoformat(timespec="seconds")))
    folder = os.path.join(DATASET, str(sid))
    os.makedirs(folder, exist_ok=True)
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Camera unavailable.")
        with connect() as c: c.execute("DELETE FROM students WHERE student_id=?", (sid,))
        return
    d, count = detector(), 0
    print("Look at the camera. Press Q to stop early.")
    try:
        while count < SAMPLES:
            ok, frame = cam.read()
            if not ok: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found = d.detectMultiScale(gray, 1.2, 5, minSize=(80,80))
            for x,y,w,h in found[:1]:
                face = cv2.resize(gray[y:y+h, x:x+w], SIZE)
                count += 1
                cv2.imwrite(os.path.join(folder, f"{count:03}.jpg"), face)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame, f"Samples {count}/{SAMPLES}", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,0), 2)
            cv2.imshow("Register - Q to quit", frame)
            if cv2.waitKey(100) & 0xFF in (ord("q"), ord("Q")): break
    finally:
        cam.release(); cv2.destroyAllWindows()
    print(f"Captured {count} samples for {name}. Choose train before attendance.")

def train():
    if not hasattr(cv2, "face"):
        print("Install opencv-contrib-python; cv2.face is missing."); return
    faces, labels = [], []
    with connect() as c: students = c.execute("SELECT student_id FROM students").fetchall()
    for (sid,) in students:
        folder = os.path.join(DATASET, str(sid))
        if not os.path.isdir(folder): continue
        for fn in os.listdir(folder):
            if not fn.lower().endswith((".jpg",".jpeg",".png")): continue
            img = cv2.imread(os.path.join(folder,fn), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces.append(cv2.resize(img, SIZE)); labels.append(sid)
    if len(faces) < 2:
        print("Register a student and capture at least two samples first."); return
    rec = cv2.face.LBPHFaceRecognizer_create()
    rec.train(faces, np.array(labels, dtype=np.int32)); rec.write(MODEL)
    print(f"Model trained using {len(faces)} samples.")

def mark(sid):
    now = datetime.now()
    with connect() as c:
        row = c.execute("SELECT name FROM students WHERE student_id=?", (int(sid),)).fetchone()
        if not row: return "Unknown student"
        try:
            c.execute("INSERT INTO attendance(student_id,attendance_date,attendance_time) VALUES(?,?,?)",
                      (int(sid), date.today().isoformat(), now.strftime("%H:%M:%S")))
            return f"Attendance marked: {row[0]}"
        except sqlite3.IntegrityError:
            return f"Already marked today: {row[0]}"

def attendance_camera():
    if not os.path.exists(MODEL):
        print("Train the model first."); return
    if not hasattr(cv2, "face"):
        print("Install opencv-contrib-python."); return
    rec = cv2.face.LBPHFaceRecognizer_create(); rec.read(MODEL)
    cam = cv2.VideoCapture(0)
    if not cam.isOpened(): print("Camera unavailable."); return
    d, message = detector(), ""
    print("Camera running; press Q to quit.")
    try:
        while True:
            ok, frame = cam.read()
            if not ok: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for x,y,w,h in d.detectMultiScale(gray,1.2,5,minSize=(80,80)):
                label, confidence = rec.predict(cv2.resize(gray[y:y+h,x:x+w], SIZE))
                with connect() as c:
                    row = c.execute("SELECT name FROM students WHERE student_id=?", (int(label),)).fetchone()
                if row and confidence <= THRESHOLD:
                    caption, color = row[0], (0,180,0)
                    message = mark(label)
                else: caption, color = "Unknown", (0,0,255)
                cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
                cv2.putText(frame,f"{caption} ({confidence:.0f})",(x,max(25,y-10)),
                            cv2.FONT_HERSHEY_SIMPLEX,.6,color,2)
            if message:
                cv2.putText(frame,message[:55],(10,30),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,0),2)
            cv2.imshow("Smart Attendance - Q to quit",frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"),ord("Q")): break
    finally:
        cam.release(); cv2.destroyAllWindows()

def report():
    chosen = input("Date YYYY-MM-DD (blank=today): ").strip() or date.today().isoformat()
    with connect() as c:
        rows = c.execute("""SELECT s.student_id,s.name,s.department,a.attendance_date,a.attendance_time
            FROM attendance a JOIN students s ON s.student_id=a.student_id
            WHERE a.attendance_date=? ORDER BY a.attendance_time""", (chosen,)).fetchall()
    print("\\nReport:", chosen)
    for row in rows: print(" | ".join(map(str,row)))
    if not rows: print("No records found.")

def main():
    setup()
    while True:
        print("\\n=== SMART ATTENDANCE ===\\n1 Register student\\n2 Train model\\n3 Mark attendance\\n4 View report\\n5 List students\\n0 Exit")
        choice = input("Choose: ").strip()
        if choice == "1": register()
        elif choice == "2": train()
        elif choice == "3": attendance_camera()
        elif choice == "4": report()
        elif choice == "5":
            with connect() as c: rows = c.execute("SELECT student_id,name,department FROM students ORDER BY student_id").fetchall()
            print(*rows, sep="\\n") if rows else print("No students registered.")
        elif choice == "0": break
        else: print("Invalid option.")
if __name__ == "__main__":
    setup()
    main()
