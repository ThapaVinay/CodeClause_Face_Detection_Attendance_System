import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://facedetectionattendance-89f06-default-rtdb.firebaseio.com/"

})


ref = db.reference('Students')

data = {
    "666666" : {
        "name" : "vinay thapa",
        "major" : "btech cse",
        "starting_year" : 2021,
        "total_attendance" : 6,
        "standing" : "G",
        "year" : 3,
        "last_attendance_time" : "2023-07-13 00:54:34"

    },

    "321654" : {
        "name" : "murtaza",
        "major" : "btech cse",
        "starting_year" : 2021,
        "total_attendance" : 6,
        "standing" : "G",
        "year" : 3,
        "last_attendance_time" : "2023-07-13 00:54:34"

    },

    "852741" : {
        "name" : "emily blunt",
        "major" : "btech cse",
        "starting_year" : 2021,
        "total_attendance" : 6,
        "standing" : "G",
        "year" : 3,
        "last_attendance_time" : "2023-07-13 00:54:34"

    },

    "963852" : {
        "name" : "elon musk",
        "major" : "btech cse",
        "starting_year" : 2021,
        "total_attendance" : 6,
        "standing" : "G",
        "year" : 3,
        "last_attendance_time" : "2023-07-13 00:54:34"

    }
}

for key, value in data.items():
    ref.child(key).set(value)


