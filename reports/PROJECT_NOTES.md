# Project Notes

**Aim:** automate attendance using webcam-based face detection and recognition.

**Workflow:** register student and capture samples -> train LBPH model -> recognize face -> save daily attendance -> print report.

**Entities:** `students` and `attendance`. One student can have attendance records on multiple dates. A unique constraint prevents duplicate records for one student on the same date.

**Test checklist**
- [ ] Register a consenting test student and capture samples.
- [ ] Train the model.
- [ ] Test recognition in normal lighting.
- [ ] Test an unregistered face.
- [ ] Confirm duplicate attendance is prevented.
- [ ] Generate a date-based report.
- [ ] Document camera/lighting limitations.

**Privacy:** do not commit actual student face images, database files, or trained models to a public repository.
