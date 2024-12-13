from pymongo import MongoClient


client = MongoClient("mongodb+srv://parthbapodara:GVgjS7sz3kwJpl4W@cluster0.ywy8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client.class_subject_db

collection_name = db["School_Management_Collection"]
