import os
import pyautogui
tempscreen = pyautogui.screenshot()
tempscreen.save("temp.png")
pyautogui.sleep(0.5)
os.startfile("test2.py")