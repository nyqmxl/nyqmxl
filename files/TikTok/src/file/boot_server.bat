@echo off

pip install pymongo streamlit websockets pyotp numpy opencv-python selenium pillow pyautogui psutil urllib3 numpy

start /min python mq.py
start /min python network_server.py
start /min python network_admin.py
start /min python network_client.py
start /min streamlit run ui_streamlit.py

pause