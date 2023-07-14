''' libraries to install
    1. cmake
    2. dlib
    3. face-recognition
    4. cvzone
    5. opencv 

    Modes :
    0. Marked
    1. Already Marked
    2. Details window
    3. Active
'''

import numpy as np
import cv2
import os
import pickle
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# connection with the firebase
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://facedetectionattendance-89f06-default-rtdb.firebaseio.com/",
    'storageBucket' : "facedetectionattendance-89f06.appspot.com"

})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

imgBackground = cv2.imread('./resources/background.png')

# importing the mode images into a list
folderModePath = './resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []
for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(imgModeList)


# load the encoding files
# print("Loading Encode file ...")
file = open('encodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
# print("Encode file Loaded ...")

modeType = 3
counter = 0
id = -1

# display the webcam
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    # face recognition uses RGB color code
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # it will find the encodings for the current image
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # overlaying webcam on the image
    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
    cv2.waitKey(1)

    if faceCurFrame:
        if(counter ==0 ):
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                # finds the euclidean distance between the encodings
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                # print("matches", matches)
                # print("matches", faceDis)x``

                matchIndex = np.argmin(faceDis)
                if (matches[matchIndex]):
                    # print(studentIds[matchIndex])

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    bbox = 55 + x1, 162 + y1, x2-x1, y2-y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = studentIds[matchIndex]

                    if counter == 0:
                        cvzone.putTextRect(imgBackground, "Loading", (275,400))
                        cv2.imshow("Face Attendance", imgBackground)
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 2

        if counter != 0:

            # download the data from firebase
            if counter == 1:

                # Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                # print(studentInfo)

                # Get the image from the storage
                blob = bucket.get_blob(f'./images/{id}.jpeg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2RGB)
                
                # update data of attendence
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                # print(secondsElapsed)

                if secondsElapsed > 6:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 1
                    counter = 0
                    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

            if modeType != 1:
                if 10 < counter < 20:
                    modeType = 0

                imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

                if counter <= 10:
                    # adding the different details to the graphics
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861,125), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)

                    # setting the width for the name
                    (w,h) , _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1,1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (50,50,50), 1)

                    # setting the image
                    imgBackground[175:175+216, 909:909+216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 3
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

    else:
        modeType = 3
        counter = 0


    cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) == 13:  # ASCII code for enter key
        break
