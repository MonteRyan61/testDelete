import streamlit as st
import speech_recognition as sr
from PIL import Image
import os

# Stuff for MongoDB Comunication
import pymongo
from decouple import config
from datetime import datetime
import certifi

CLIENT = pymongo.MongoClient(config('ATLAS_URI'), tlsCAFile=certifi.where())
DB = CLIENT["music_list"]
OUTPUTS = DB["outputs"]

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

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=2, phrase_time_limit=2)
        if audio:
            try:
                txt = r.recognize_google(audio)
                return txt
            except:
                st.write(f"<div style='text-align:center;'>Audio not recognized. Try again!</div>", unsafe_allow_html=True)
        else:
            st.write(f"<div style='text-align:center;'>Audio not recognized. Try again!</div>", unsafe_allow_html=True)


def checkText(mytxt):
    mytxt = mytxt.split(' ')
    if 'happy' in mytxt:
        return 1, 'happy'
    elif 'sad' in mytxt:
        return 2, 'sad'
    elif 'angry' in mytxt:
        return 3, 'angry'
    elif 'surprised' in mytxt:
        return 4, 'surprise'
    elif 'neutral' in mytxt:
        return 5, 'neutral'
    else:
        return -1, ''

def main():
    # Get the current working directory
    cwd = os.getcwd()

    # Specify the image path relative to the current working directory
    image_path = os.path.join(cwd, 'microphone-solid.png')

    # Open the image using PIL
    # img = Image.open(image_path)

    # Display the image using Streamlit
    # st.image(img, width=25)
    
    #get the date to keep track of most recent call from mongo
    now = datetime.now()
    st.write('<style>div.stButton > button:first-child { %s }</style>' % button_style, unsafe_allow_html=True)
    

    if st.button('Click to record audio'):
        st.write(f"<div style='text-align:center;'>Say your mood (happy, sad, angry, surprised, neutral)</div>", unsafe_allow_html=True)
        txt = get_audio()
        print(txt)
        if txt:
            return_flag, genre = checkText(txt)
            print(return_flag)

            if return_flag != -1:
                OUTPUTS.insert_one({"name": txt, "createdAt": now})
                st.write(f"<div style='text-align:center; font-size: 24px;'><b>{genre.capitalize()}</b> confirmed </div>", unsafe_allow_html=True)
            else:
                st.write(f"<div style='text-align:center;'>Please try again!</div>", unsafe_allow_html=True)

            return return_flag
        else:
           st.write(f"<div style='text-align:center;'>Say your mood (happy, sad, angry, surprised, neutral)</div>", unsafe_allow_html=True)
            

main()