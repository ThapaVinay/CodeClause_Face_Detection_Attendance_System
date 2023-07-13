''' libraries to install
    1. cmake
    2. dlib
    3. face-recognition
    4. cvzone
    5. opencv 
'''

import numpy as np
import cv2
import os
import pickle
import face_recognition
import cvzone

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
print("Loading Encode file ...")
file = open('encodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode file Loaded ...")


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
    imgBackground[44:44+633, 808:808+414] = imgModeList[0]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        # finds the euclidean distance between the encodings
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("matches", matches)
        # print("matches", faceDis)

        matchIndex = np.argmin(faceDis)
        if (matches[matchIndex]):
            # print(studentIds[matchIndex])

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            bbox = 55 + x1, 162 + y1, x2-x1, y2-y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

    cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) == 13:  # ASCII code for enter key
        break
