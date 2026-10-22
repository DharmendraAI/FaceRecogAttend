-- Reference schema. The application creates these tables in SQLite automatically.
CREATE TABLE students (
  student_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE attendance (
  attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  attendance_date TEXT NOT NULL,
  attendance_time TEXT NOT NULL,
  FOREIGN KEY(student_id) REFERENCES students(student_id),
  UNIQUE(student_id, attendance_date)
);
