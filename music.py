import streamlit as st
import time
from streamlit_webrtc import webrtc_streamer
import av
import cv2 
import numpy as np 
import mediapipe as mp 
from keras.models import load_model
import webbrowser

# Stuff for MongoDB Comunication
import pymongo
from decouple import config
from datetime import datetime
import certifi

CLIENT = pymongo.MongoClient(config('ATLAS_URI'), tlsCAFile=certifi.where())
DB = CLIENT["music_list"]
OUTPUTS = DB["outputs"]

model  = load_model("model.h5")
label = np.load("labels.npy")
holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils


#CSS styles
CSS = """

html{
	background: #EDD8C5;
}

h2 {
    color: black;
    text-align: center;
    font-size: 3.8vw;
}
p {
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 25px;
}
.css-fg4pbf {
	background: #EDD8C5;
}

.css-18ni7ap {
	background: #EDD8C5;
}

.css-1dp5vir {
	height: 0px;
}

.css-fg4pbf {
	align-items: center;
    justify-content: center;
}
"""

button_style = """
    display: block;
    margin: 0 auto;
    width: 200px;
    height: 70px;
    background: rgba(163, 101, 109, 0.5);
    box-shadow: 0px 4px 11px rgba(0, 0, 0, 0.25);
    font-family: Caraque Regular Melted, cursive;
    font-size: 25px;
    margin-bottom: 1vw;
"""

# Hide the navigation menu and "Made with Streamlit" footer
hide_menu_css_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_css_style, unsafe_allow_html=True)
st.markdown(f'<style>{CSS}</style>', unsafe_allow_html=True)

if "run" not in st.session_state:
	st.session_state["run"] = "true"

try:
	emotion = np.load("emotion.npy")[0]
except:
	emotion=""


class EmotionProcessor:
	def recv(self, frame):
		frm = frame.to_ndarray(format="bgr24")

		##############################
		frm = cv2.flip(frm, 1)
  

		res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

		lst = []

		if res.face_landmarks:
			for i in res.face_landmarks.landmark:
				lst.append(i.x - res.face_landmarks.landmark[1].x)
				lst.append(i.y - res.face_landmarks.landmark[1].y)

			if res.left_hand_landmarks:
				for i in res.left_hand_landmarks.landmark:
					lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
					lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
			else:
				for i in range(42):
					lst.append(0.0)

			if res.right_hand_landmarks:
				for i in res.right_hand_landmarks.landmark:
					lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
					lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
			else:
				for i in range(42):
					lst.append(0.0)

			lst = np.array(lst).reshape(1,-1)

			pred = label[np.argmax(model.predict(lst))]
   			
			print(pred)
			cv2.putText(frm, pred.capitalize(), (300,100),cv2.FONT_ITALIC, 1, (0,0,0),2)

			np.save("emotion.npy", np.array([pred]))

			
			drawing.draw_landmarks(
									frm, 
									res.face_landmarks, 
									holistic.FACEMESH_CONTOURS, #alot of options here to make it look better holistic.FACEMESH_TESSELATION
									landmark_drawing_spec=drawing.DrawingSpec(
										color=(200, 200, 200),  # Light gray color
										thickness=1,  # Line thickness
										circle_radius=1),  # Circle radius for each landmark point
									connection_drawing_spec=drawing.DrawingSpec(
										color=(255, 255, 153),  # Pale yellow color
										thickness=1))  # Line thickness for landmark connections
		# drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
		# drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

		##############################
		return av.VideoFrame.from_ndarray(frm, format="bgr24")
 
    
   

webrtc_streamer(key="example", desired_playing_state=True, async_processing=True,
					video_processor_factory=EmotionProcessor)

st.write('<style>div.stButton > button:first-child { %s }</style>' % button_style, unsafe_allow_html=True)
btn = st.button("Capture Emotion")

now = datetime.now()

if btn:
	if not(emotion):
		st.warning(f"<div style='text-align:center;'>Please capture your emotion first</div>", unsafe_allow_html=True)
		st.session_state["run"] = "true"
	else:
		print("EMOTION OUTPUT " + emotion)
		st.write(f"<div style='text-align:center; font-size: 24px;'><b>{emotion.capitalize()}</b> confirmed </div>", unsafe_allow_html=True)
		#Update mongodb with the newly scanned motion
		OUTPUTS.insert_one({"name": emotion, "createdAt": now})
		np.save("emotion.npy", np.array([""]))
		st.session_state["run"] = "false"