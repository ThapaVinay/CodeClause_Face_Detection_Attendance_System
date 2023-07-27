from flask import Flask, render_template, Response
import cv2
import numpy as np
import os
import pickle
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import time

    # connection with the firebase
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facedetectionattendance-89f06-default-rtdb.firebaseio.com/",
    'storageBucket': "facedetectionattendance-89f06.appspot.com"

})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)


# importing the mode images into a list
folderModePath = './resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []
for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

file = open('encodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds

id = -1 

faceCurFrame = []
encodeCurFrame = []

app = Flask(__name__)
attendance_status = ""
attendance_color = (0, 0, 255)  # Red color for "Not Marked"

# Set the interval in seconds for face detection
FACE_DETECTION_INTERVAL = 5  # Adjust this interval as needed (e.g., 5 seconds)

def generate_frames():
    last_detection_time = time.time()  # Initialize the last detection time

    while True:
        global attendance_status, attendance_color
        # read the camera frame
        success, frame = cap.read()
        if not success:
            break
        else:
            # Check if it's time for face detection based on the interval
            current_time = time.time()
            if current_time - last_detection_time >= FACE_DETECTION_INTERVAL:
                last_detection_time = current_time  # Update the last detection time

                imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                # it will find the encodings for the current image
                faceCurFrame = face_recognition.face_locations(imgS)
                encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
                for encodeFace in encodeCurFrame:
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                    matchIndex = np.argmin(faceDis)
                    if (matches[matchIndex]):
                        id = studentIds[matchIndex]

                        # Get the data
                        studentInfo = db.reference(f'Students/{id}').get()

                        attendance_color = (0, 0, 255)
                        attendance_status = f"Marked  {studentInfo['name']}  Attendence:{studentInfo['total_attendance']}"

                        # update data of attendence
                        datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                        if secondsElapsed > 60:
                            ref = db.reference(f'Students/{id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            cv2.putText(frame, attendance_status, (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1, attendance_color, 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
