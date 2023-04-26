import streamlit as st
import cv2
import pymongo
from decouple import config
from datetime import datetime
import certifi

CLIENT = pymongo.MongoClient(config('ATLAS_URI'), tlsCAFile=certifi.where())
DB = CLIENT["music_list"]
OUTPUTS = DB["outputs"]

def main():
    now = datetime.now()
    st.title("Webcam Test")
    run = st.checkbox('Run')
    video_feed = st.empty()
    
    OUTPUTS.insert_one({"name": "test", "createdAt": now})
    
    if run:
        cap = cv2.VideoCapture(0)
        while run:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture frame from camera.")
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_feed.image(frame)
        cap.release()
        
        

if __name__ == '__main__':
    main()