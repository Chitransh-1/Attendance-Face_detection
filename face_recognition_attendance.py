import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime

# Step 1: Load known faces and their names
def load_known_faces(known_faces_dir):
    known_faces = []
    known_names = []
    for name in os.listdir(known_faces_dir):
        person_dir = os.path.join(known_faces_dir, name)
        for filename in os.listdir(person_dir):
            image_path = os.path.join(person_dir, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(name)
    return known_faces, known_names

# Step 2: Initialize video capture
def initialize_video_capture():
    video_capture = cv2.VideoCapture(0)
    return video_capture

# Step 3: Recognize faces and mark attendance
def recognize_faces_and_mark_attendance(video_capture, known_faces, known_names):
    attendance_log = set()
    while True:
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_faces, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]

            if name != "Unknown" and name not in attendance_log:
                attendance_log.add(name)
                with open("attendance_log.csv", "a") as log_file:
                    now = datetime.now()
                    log_file.write(f"{name},{now.strftime('%Y-%m-%d %H:%M:%S')}\n")

            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    known_faces_dir = "known_faces"
    known_faces, known_names = load_known_faces(known_faces_dir)
    video_capture = initialize_video_capture()
    recognize_faces_and_mark_attendance(video_capture, known_faces, known_names)
