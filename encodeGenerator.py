import cv2
import face_recognition
import pickle
import os 

# importing the student images into a list 
folderPath = './images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])   # splits the text from .png


def findEncodings(imagesList):
    
    encodeList = []
    for image in imagesList:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # face recognition uses RGB color code
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    
    return encodeList

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding completed ...")

print(encodeListKnownWithIds)


file = open("encodeFile.p", "wb")
pickle.dump(encodeListKnownWithIds, file)  # converts into serialised form for export over network
file.close()
print("File saved successfully")

