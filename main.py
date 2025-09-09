#-----------------------Library Init-----------------------
import pyautogui as auto
from pynput import keyboard, mouse
import time
import tkinter as tk
from tkinter import ttk, PhotoImage, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import ast
import math
import os
import sys
import customtkinter as ctk

#-----------------------Program Init-----------------------
# List to store recorded key events
auto.PAUSE = 0

#-----------------------Variable Init-----------------------
actionList = []
recording = False
recordedActionList = []
customKeyActionsList = []
validDriveTrains = ["Tank", "Mecanum", "Fortnite"]
lastClick = []
recordedClick = []
recordingMouseClick = False
bypassNoMouseRefocus = False

#-----------------------Functions-----------------------
def on_press(key):
    try:
        # For alphanumeric keys
        key_char = key.char
    except AttributeError:
        # For special keys (e.g., Key.space, Key.esc)
        key_char = str(key)
    
    # Checks if an action before it was spam
    if len(actionList) > 0:
        if actionList[-1][1] != key_char or actionList[-1][0] != "pressed":
            actionList.append(('pressed', key_char, time.time()))
            print(f"Key pressed: {key_char}")
    else:
        actionList.append(('pressed', key_char, time.time()))
        print(f"Key pressed: {key_char}")


def on_release(key):
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    actionList.append(('released', key_char, time.time()))
    print(f"Key released: {key_char}")

    # Stop listener when 'Esc' is pressed
    if key == keyboard.Key.esc:
        print("Keyboard listener stopped.")
        return False

 
def on_click(x, y, button, pressed):
    if pressed:
        lastClick = [(x, y), str(button)]

        global recordingMouseClick
        if lastClick != [] and "Button.left" == lastClick[1] and recordingMouseClick:
            global recordedClick

            recordingMouseClick = False 
            recordedClick.clear()
            recordedClick = lastClick.copy()
            mouseFocusOutput.delete(0, ctk.END)
            mouseFocusOutput.insert(0, recordedClick)
        print(lastClick)


def resourcePath(relativePath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller stores temp unpacked files here
        return os.path.join(sys._MEIPASS, relativePath)
    return os.path.join(os.path.abspath("."), relativePath)


def record():
    global recordedActionList
    global actionList
    global recording

    if recording:
        recording = False
        recordedActionList = actionList.copy()
        actionsBox.delete(0, ctk.END)
        actionsBox.insert(0, str(recordedActionList))
        print(recordedActionList)
        recordingButton.configure(text="Start")
    else:
        recording = True
        actionList.clear()
        recordingButton.configure(text="Stop")


def copyActions():
    # Copies the given recorded action list to the Clipboard
    root.clipboard_clear()
    root.clipboard_append(str(recordedActionList))


def playRecording():
    global bypassNoMouseRefocus 

    if recordedClick != []:
        auto.click(x=recordedClick[0][0], y=recordedClick[0][1])
    elif bypassNoMouseRefocus == False:
        messagebox.showinfo("Warning", "Recording will play without a mouse refocus. \n Create a mouse refocus or press play again to replay recording.")
        bypassNoMouseRefocus = True
        return

    # Replays the recorded actions
    playButton.configure(text="Playing")
    for event in recordedActionList:
        if recordedActionList.index(event) != len(recordedActionList)-1:
            if event[0] == "pressed":
                auto.keyDown(str(event[1]))
            if event[0] == "released":
                auto.keyUp(str(event[1]))
            time.sleep(recordedActionList[recordedActionList.index(event)+1][2] - event[2])
        else:
            if event[0] == "released":
                auto.keyUp(str(event[1]))
    playButton.configure(text="Play")


def threadManager(thread):
    if thread == "replayRecording":
        try:
            global recordedActionList
            recordedActionList = ast.literal_eval(replayInput.get())
            print(recordedActionList)

            # Gives the play recording a seperate thread from the main thread
            playRecordingThread = threading.Thread(target=playRecording)
            playRecordingThread.daemon = True
            playRecordingThread.start() # Yay multi-threading! Took me so long to figure that out :(
        except:
            replayInput.insert(0, "Invalid String")
        
    elif thread == "playRecording":
        playRecordingThread = threading.Thread(target=playRecording)
        playRecordingThread.daemon = True
        playRecordingThread.start()

    elif thread == "createFunction":
        playRecordingThread = threading.Thread(target=createFunction)
        playRecordingThread.daemon = True
        playRecordingThread.start()


def savePath(data):
    saveCustomInput.delete(0, ctk.END)
    file_types = [('Text files', '*.txt'), ('All files', '*.*')]
    file = filedialog.asksaveasfile(mode='w', filetypes=file_types, defaultextension=".txt", initialfile="myPath")
    if file: # Check if the user didn't cancel the dialog
        content_to_save = str(data)
        file.write(content_to_save)
        file.close()
        messagebox.showinfo("File Saved", "The path has been saved.")

def loadPath():
    global recordedActionList

    # Open a file dialog to let the user select a file
    filepath = filedialog.askopenfilename(
        initialdir="/",  # Optional: Set the initial directory
        title="Select a file",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*")) # Optional: Filter file types
    )

    if filepath:  # If a file was selected
        try:
            with open(filepath, 'r') as file:
                content = file.read()
                # Process the content (e.g., load into a Text widget, parse data)
                try:
                    recordedActionList = ast.literal_eval(content)
                except:
                    messagebox.showinfo("Warning", "Error: Cannot read path. \n Please ensure the file is valid.")
        except Exception as e:
            print(f"Error loading file: {e}")


def getMecanumThrottles(horizontalAxis, verticalAxis, rotationalAxis):
    angleRadians = math.atan2(horizontalAxis, verticalAxis)
    
    if horizontalAxis != 0 or verticalAxis != 0:
        fl_throttle = math.cos(angleRadians) + math.sin(angleRadians) + rotationalAxis
        fr_throttle = math.cos(angleRadians) - math.sin(angleRadians) - rotationalAxis
        bl_throttle = math.cos(angleRadians) - math.sin(angleRadians) + rotationalAxis
        br_throttle = math.cos(angleRadians) + math.sin(angleRadians) - rotationalAxis

        fl_throttle = round(fl_throttle, 15)
        fr_throttle = round(fr_throttle, 15)
        bl_throttle = round(bl_throttle, 15)
        br_throttle = round(br_throttle, 15)
    else:
        fl_throttle = 0 + rotationalAxis
        fr_throttle = 0 - rotationalAxis
        bl_throttle = 0 + rotationalAxis
        br_throttle = 0 - rotationalAxis

    # Normalize throttles
    max_throttle = max(abs(fl_throttle), abs(fr_throttle), abs(bl_throttle), abs(br_throttle))
    max_throttle = round(max_throttle, 15)
    if max_throttle > 1.0:
        fl_throttle /= max_throttle
        fr_throttle /= max_throttle
        bl_throttle /= max_throttle
        br_throttle /= max_throttle

    return fl_throttle, fr_throttle, bl_throttle, br_throttle


def updateMecanumMotors(throttles, stateChange, movement):
    global resultFunction

    # Updates motors
    resultFunction += "\n"
    resultFunction += "\n   // Update throttles to " + stateChange + " " + movement
    resultFunction += "\n   frontLeftMotor.set(" + str(throttles[0]) + ");"
    resultFunction += "\n   frontRightMotor.set(" + str(throttles[1]) + ");"
    resultFunction += "\n   backLeftMotor.set(" + str(throttles[2]) + ");"
    resultFunction += "\n   backRightMotor.set(" + str(throttles[3]) + ");"


def addDelay(event):
    global resultFunction
    
    if recordedActionList.index(event) != len(recordedActionList) - 1 and len(recordedActionList) > 1:
        resultFunction += "\n   delay(" + str(round((recordedActionList[recordedActionList.index(event)+1][2] - event[2]) * 1000)) + ");"


def createFunction():
    userInput = functionNameBox.get()
    driveTrain = driveTrainInput.get()
    global resultFunction
    resultFunction = ""

    # Get Path Name
    if userInput != "":
        try:
            pathName = ''.join(char for char in userInput if char.isalnum())
            print(pathName)
        except:
            pathName = "myPath"
    else:
        pathName = "myPath"
    
    if driveTrain != "" and driveTrain in validDriveTrains:
        pass
    elif driveTrain == "":
        messagebox.showinfo("Warning", "Error: No drivetrain selected. \n Please select a drivetrain.")
        return
    elif not driveTrain in validDriveTrains:
        messagebox.showinfo("Warning", "Error: Invalid drivetrain. \n Please ensure the drivetrain is correct.")
        return
    

    # Loop for every event happened
    if driveTrain.lower() == "mecanum":
        hAxis = 0
        vAxis = 0
        rAxis = 0

        resultFunction += "void " + pathName + "(NoU_Motor frontLeftMotor, NoU_Motor frontRightMotor, NoU_Motor backLeftMotor, NoU_Motor backRightMotor) {"
        for event in recordedActionList:
            if event[0] == "pressed":
                if event[1].lower() == "w":
                    vAxis += 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "include", "moving forward")

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "s":
                    vAxis -= 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "include", "moving backward")

                    # Checks if a delay can be put
                    addDelay(event)

                elif event[1].lower() == "a":
                    hAxis -= 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "include", "moving left")

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "d":
                    hAxis += 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "include", "moving right")

                    # Checks if a delay can be put
                    addDelay(event)

                elif event[1].lower() == "j":
                    rAxis -= 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "include", "turning left")

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "l":
                    rAxis += 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "include", "turning right")

                    # Checks if a delay can be put
                    addDelay(event)
                
                else:
                    # Checks for custom key actions and adds the code
                    for action in customKeyActionsList:
                        if action[0] == event[1]:
                            resultFunction += "\n"
                            resultFunction += "\n   // Custom action call"
                            resultFunction += "\n   " + action[1]

            elif event[0] == "released":
                if event[1].lower() == "w":
                    vAxis -= 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "remove", "moving forward")

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "s":
                    vAxis += 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "remove", "moving backward")

                    # Checks if a delay can be put
                    addDelay(event)

                elif event[1].lower() == "a":
                    hAxis += 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "remove", "moving left")

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "d":
                    hAxis -= 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "remove", "moving right")

                    # Checks if a delay can be put
                    addDelay(event)

                elif event[1].lower() == "j":
                    rAxis += 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "remove", "turning left")

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "l":
                    rAxis -= 1

                    # Calculates throttles and updates motors
                    throttleList = getMecanumThrottles(hAxis, vAxis, rAxis)
                    updateMecanumMotors(throttleList, "remove", "turning right")

                    # Checks if a delay can be put
                    addDelay(event)
                
                else:
                    # Checks for custom key actions and adds the code
                    for action in customKeyActionsList:
                        if action[0] == event[1]:
                            resultFunction += "\n"
                            resultFunction += "\n   // Custom action call"
                            resultFunction += "\n   " + action[1]

                    # Checks if a delay can be put
                    addDelay(event)
        resultFunction += "\n}"


    if driveTrain.lower() == "tank":
        resultFunction += "void " + pathName + "(NoU_Motor frontLeftMotor, NoU_Motor frontRightMotor, NoU_Motor backLeftMotor, NoU_Motor backRightMotor) {"
        for event in recordedActionList:
            if event[0] == "pressed":
                if event[1].lower() == "w":
                    # Sets motors to move forward
                    resultFunction += "\n"
                    resultFunction += "\n   // Move Forward"
                    resultFunction += "\n   frontLeftMotor.set(1);"
                    resultFunction += "\n   frontRightMotor.set(1);"
                    resultFunction += "\n   backLeftMotor.set(1);"
                    resultFunction += "\n   backRightMotor.set(1);"

                    #Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "s":
                    # Sets motors to move backward
                    resultFunction += "\n"
                    resultFunction += "\n   // Move Backward"
                    resultFunction += "\n   frontLeftMotor.set(-1);"
                    resultFunction += "\n   frontRightMotor.set(-1);"
                    resultFunction += "\n   backLeftMotor.set(-1);"
                    resultFunction += "\n   backRightMotor.set(-1);"

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "a":
                    # Sets motors to turn left
                    resultFunction += "\n"
                    resultFunction += "\n   // Turn Left"
                    resultFunction += "\n   frontLeftMotor.set(-1);"
                    resultFunction += "\n   frontRightMotor.set(1);"
                    resultFunction += "\n   backLeftMotor.set(-1);"
                    resultFunction += "\n   backRightMotor.set(1);"

                    #Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "d":
                    # Sets motors to turn right
                    resultFunction += "\n"
                    resultFunction += "\n   // Turn Right"
                    resultFunction += "\n   frontLeftMotor.set(1);"
                    resultFunction += "\n   frontRightMotor.set(-1);"
                    resultFunction += "\n   backLeftMotor.set(1);"
                    resultFunction += "\n   backRightMotor.set(-1);"

                    # Checks if a delay can be put
                    addDelay(event)
                
                else:
                    # Checks for custom key actions and adds the code
                    for action in customKeyActionsList:
                        if action[0] == event[1]:
                            resultFunction += "\n"
                            resultFunction += "\n   // Custom action call"
                            resultFunction += "\n   " + action[1]
                    
                    # Checks if a delay can be put
                    addDelay(event)

            elif event[0] == "released" and (event[1].lower() == "w" or event[1].lower() == "a" or event[1].lower() == "s" or event[1].lower() == "d"):
                # Stops all motors
                resultFunction += "\n"
                resultFunction += "\n   // Stop All Motors"
                resultFunction += "\n   frontLeftMotor.set(0);"
                resultFunction += "\n   frontRightMotor.set(0);"
                resultFunction += "\n   backLeftMotor.set(0);"
                resultFunction += "\n   backRightMotor.set(0);"

                # Checks if a delay can be put
                addDelay(event)
        resultFunction += "\n}"


    if driveTrain.lower() == "fortnite":
        resultFunction += "void " + pathName + "(NoU_Motor frontLeftMotor, NoU_Motor frontRightMotor, NoU_Motor backLeftMotor, NoU_Motor backRightMotor) {"
        for event in recordedActionList:
            if event[0] == "pressed":
                if event[1].lower() == "w":
                    # Sets motors to move forward
                    resultFunction += "\n"
                    resultFunction += "\n   // Rotate To Wailing Woods"
                    resultFunction += "\n   Serial.Print('Wailing Woods');"
                    resultFunction += "\n   frontLeftMotor.set(-1);"
                    resultFunction += "\n   frontRightMotor.set(1);"
                    resultFunction += "\n   backLeftMotor.set(-1);"
                    resultFunction += "\n   backRightMotor.set(1);"

                    #Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "s":
                    # Sets motors to move backward
                    resultFunction += "\n"
                    resultFunction += "\n   // Rotate To Salty Springs"
                    resultFunction += "\n   Serial.Print('Salty Springs');"
                    resultFunction += "\n   frontLeftMotor.set(1);"
                    resultFunction += "\n   frontRightMotor.set(-1);"
                    resultFunction += "\n   backLeftMotor.set(1);"
                    resultFunction += "\n   backRightMotor.set(-1);"

                    # Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "a":
                    # Sets motors to turn left
                    resultFunction += "\n"
                    resultFunction += "\n   // Rotate to Anarchy Acres"
                    resultFunction += "\n   Serial.Print('Anarchy Acres');"
                    resultFunction += "\n   frontLeftMotor.set(1);"
                    resultFunction += "\n   frontRightMotor.set(-1);"
                    resultFunction += "\n   backLeftMotor.set(1);"
                    resultFunction += "\n   backRightMotor.set(-1);"

                    #Checks if a delay can be put
                    addDelay(event)
                
                elif event[1].lower() == "d":
                    # Sets motors to turn right
                    resultFunction += "\n"
                    resultFunction += "\n   // Rotate to Dusty Divots"
                    resultFunction += "\n   Serial.Print('Dusty Divots');"
                    resultFunction += "\n   frontLeftMotor.set(-1);"
                    resultFunction += "\n   frontRightMotor.set(1);"
                    resultFunction += "\n   backLeftMotor.set(-1);"
                    resultFunction += "\n   backRightMotor.set1);"

                    # Checks if a delay can be put
                    addDelay(event)
                
                else:
                    # Checks for custom key actions and adds the code
                    for action in customKeyActionsList:
                        if action[0] == event[1]:
                            resultFunction += "\n"
                            resultFunction += "\n   // Custom action call"
                            resultFunction += "\n   " + action[1]

                    # Checks if a delay can be put
                    addDelay(event)

            elif event[0] == "released" and (event[1].lower() == "w" or event[1].lower() == "a" or event[1].lower() == "s" or event[1].lower() == "d"):
                # Stops all motors
                resultFunction += "\n"
                resultFunction += "\n   // Chat we gotta beat the storm frfrfrfrfrfr"
                resultFunction += "\n   for (int i = 0; i > 1000000; i++) {"
                resultFunction += "\n       Serial.Print('Lebron the GOAT');"
                resultFunction += "\n   }"
                resultFunction += "\n   frontLeftMotor.set(0);"
                resultFunction += "\n   frontRightMotor.set(0);"
                resultFunction += "\n   backLeftMotor.set(0);"
                resultFunction += "\n   backRightMotor.set(0);"

                # Checks if a delay can be put
                addDelay(event)
        resultFunction += "\n}"


    
    functionBox.delete("1.0", "end")
    functionBox.insert("1.0", resultFunction)


def copyFunction():
    copiedFunction = functionBox.get("1.0", "end")
    root.clipboard_clear()
    root.clipboard_append(str(copiedFunction))


def addKeyStroke():
    customKey = customKeyInput.get()
    customAction = customActionInput.get()

    if customKey != "" and len(customKey) == 1 and customAction != "" and not any(customKey in row_tuple for row_tuple in customKeyActionsList):
        customKeyActionsList.append((customKey, customAction))

        # Update remove key list
        customKeyList = []
        removeActionSelect.set("") # Also clear the displayed text
        removeActionSelect.configure(values=()) # Set the options to an empty tuple/list
        for key in customKeyActionsList:
            customKeyList.append(key[0])
        removeActionSelect.configure(values=tuple(customKeyList))

    elif customKey == "":
        messagebox.showinfo("Warning", "Error: Key empty. \n Please put the desired key in.")
    elif len(customKey) > 1:
        messagebox.showinfo("Warning", "Error: Invalid key. \n Only one character is allowed.")
    elif customAction == "":
        messagebox.showinfo("Warning", "Error: Custom action empty. \n Please put the desired code in.")
    elif any(customKey in row_tuple for row_tuple in customKeyActionsList):
        messagebox.showinfo("Warning", "Error: Key being used. \n Please put in a different key.")
    else:
        messagebox.showinfo("Warning", "Error: Undefined Exception. \n Report this error to the developer.")


def removeKeyStroke():
    keySelected = removeActionSelect.get()
    customKeyList = []

    if keySelected != "" and any(keySelected in row_tuple for row_tuple in customKeyActionsList):
        for key in customKeyActionsList:
            if key[0] == keySelected:
                del customKeyActionsList[customKeyActionsList.index(key)]

        # Update remove key list
        customKeyList = []
        removeActionSelect.set("") # Also clear the displayed text
        removeActionSelect['values'] = () # Set the options to an empty tuple/list
        for key in customKeyActionsList:
            customKeyList.append(key[0])
        removeActionSelect.configure(values=tuple(customKeyList))
    
    elif keySelected == "":
        messagebox.showinfo("Warning", "Error: No key Selected. \n Please put in a key.")
    elif not any(keySelected in row_tuple for row_tuple in customKeyActionsList):
        messagebox.showinfo("Warning", "Error: Key does not exist. \n Please put in a existing key.")
    else:
        messagebox.showinfo("Warning", "Error: Undefined Exception. \n Report this error to the developer.")


def startRecordingMouse():
    global recordingMouseClick
    recordingMouseClick = True

def changeTheme(color):
    ctk.set_appearance_mode(color)


#-----------------------Main Loop-----------------------
# Create a keyboard listener and main loop
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouseListener = mouse.Listener(on_click=on_click)
listener.start()
mouseListener.start()
print("Recording key presses. Press 'Esc' to stop.")

# Window Setup
root = ctk.CTk()
root.title("Imitate")
root.geometry("480x270")
root.resizable(False, False)

# Icon Setup
image_path = resourcePath(os.path.join("data_files", "Imitate Logo.png"))
load = Image.open(image_path)
render = ImageTk.PhotoImage(load)
root.iconphoto(False, render)

# Appearances
ctk.set_appearance_mode("light")

buttonColor = "#2e6eeb"
buttonHoverColor = "#275BBF"
entryBorderColor = "#4B7EC8"

#---Top Information---
# Actions Label
recordLabel = ctk.CTkLabel(root, text="Actions")
recordLabel.grid(row=0,column=0, columnspan=2)

# Functions Label
codeLabel =  ctk.CTkLabel(root, text="Functions")
codeLabel.grid(row=0,column=3, columnspan=2)

# Data Label
codeLabel =  ctk.CTkLabel(root, text="Data")
codeLabel.grid(row=0,column=6, columnspan=2)

# More label
moreLabel =  ctk.CTkLabel(root, text=" ")
moreLabel.grid(row=0,column=9)

# Seperators
topLabelSeperator = ctk.CTkFrame(master=root, height=1, corner_radius=0)
topLabelSeperator.grid(row=1, column=0, columnspan=12, sticky='ew', pady=5)

seperator1 = ctk.CTkFrame(master=root, width=0, corner_radius=0)
seperator1.grid(row=0, column=2, rowspan=11, sticky="ns", padx=5)

seperator2 = ctk.CTkFrame(master=root, width=0, corner_radius=0)
seperator2.grid(row=0, column=5, rowspan=11, sticky="ns", padx=5)
#---End of Top Information---


#---Row 1---
# Recording GUI
recordingLabel = ctk.CTkLabel(root, text="Record")
recordingLabel.grid(row=2,column=0)
recordingButton= ctk.CTkButton(root, text="Start", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=record)
recordingButton.grid(row=2, column=1)

# Play GUI
playLabel = ctk.CTkLabel(root, text="Play")
playLabel.grid(row=3,column=0)
playButton = ctk.CTkButton(root, text="Play", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=lambda: threadManager("playRecording"))
playButton.grid(row=3, column=1)


# Copy Actions
codeLabel =  ctk.CTkLabel(root, text="Copy Actions")
codeLabel.grid(row=4,column=0, columnspan=2)

copyActionsButton = ctk.CTkButton(root, text="Copy", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=copyActions)
copyActionsButton.grid(row=5, column=0, padx = 5)
actionsBox = ctk.CTkEntry(root, width=80, height=10, border_color=entryBorderColor)
actionsBox.grid(row=5, column=1)

# Replay GUI
replayLabel =  ctk.CTkLabel(root, text="Replay Actions")
replayLabel.grid(row=6,column=0, columnspan=2)

replayButton = ctk.CTkButton(root, text="Play", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=lambda: threadManager("replayRecording"))
replayButton.grid(row=7, column=0, padx = 5)
replayInput = ctk.CTkEntry(root, width=80, height=10, border_color=entryBorderColor)
replayInput.grid(row=7, column=1)

mouseFocusLabel = ctk.CTkLabel(root, text="Mouse Refocus")
mouseFocusLabel.grid(row=8,column=0, columnspan=2)

mouseFocusSetButton = ctk.CTkButton(root, text="Set", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=lambda: startRecordingMouse())
mouseFocusSetButton.grid(row=9, column=0, padx = 5)
mouseFocusOutput = ctk.CTkEntry(root, width=80, height=10, border_color=entryBorderColor)
mouseFocusOutput.grid(row=9, column=1)
#---End of Row 1---


#---Row 2---
# Name Input GUI
functionNameLabel = ctk.CTkLabel(root, text="Name:")
functionNameLabel.grid(row=2,column=3)
functionNameBox = ctk.CTkEntry(root, width=80, height=10, border_color=entryBorderColor)
functionNameBox.grid(row=2, column=4)

# Custom actions label
customActionsLabel = ctk.CTkLabel(root, text="Custom Actions")
customActionsLabel.grid(row=3,column=3, columnspan=2)

# Custom key GUI
addActionButton = ctk.CTkButton(root, text="Add", width=20, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=addKeyStroke)
addActionButton.grid(row=4, column=3, sticky="w")
customKeyInput = ctk.CTkEntry(root, width=30, height=10, border_color=entryBorderColor)
customKeyInput.grid(row=4, column=3, sticky="e")
customActionInput = ctk.CTkEntry(root, width=80, height=10, border_color=entryBorderColor)
customActionInput.grid(row=4, column=4, padx=5)

removeActionButton = ctk.CTkButton(root, text="Remove", width=70, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command= removeKeyStroke)
removeActionButton.grid(row=5, column=3)
removeActionSelect = ctk.CTkComboBox(root, width=80, height=10, border_color=entryBorderColor, button_color=entryBorderColor, values=(" "))
removeActionSelect.grid(row=5, column=4)

# Drivetrain input GUI
driveTrainLabel = ctk.CTkLabel(root, text="Drvtrain:")
driveTrainLabel.grid(row=6,column=3)
driveTrainInput = ctk.CTkComboBox(root, width=80, height=10, border_color=entryBorderColor, button_color=entryBorderColor, values=validDriveTrains)
driveTrainInput.grid(row=6, column=4)

# Create Function GUI
createFunctionButton = ctk.CTkButton(root, text="Create Function", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor,command=lambda: threadManager("createFunction"))
createFunctionButton.grid(row=7, column=3, columnspan=2)

functionSeperator = ctk.CTkFrame(master=root, height=1, width=1, corner_radius=0)
functionSeperator.grid(row=8, column=3, columnspan=2, sticky="ew", pady=10)

# Copy Function GUI
copyFunctionButton = ctk.CTkButton(root, text="Copy", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command = copyFunction)
copyFunctionButton.grid(row=9, column=3)
functionBox = ctk.CTkTextbox(root, width=80, height=2, border_width=2, border_color=entryBorderColor)
functionBox.grid(row=9, column=4)

# Deadspace
ifYouFoundThisThenDMTheWordCrebToNotanexpertcoderOnDiscord = ctk.CTkLabel(root, text=" ")
ifYouFoundThisThenDMTheWordCrebToNotanexpertcoderOnDiscord.grid(row=10,column=3, columnspan=2)
#---End of Row 2---


#---Row 3---
# Save & Load label
saveAndLoadLabel =  ctk.CTkLabel(root, text="Save & Load")
saveAndLoadLabel.grid(row=2,column=6, columnspan=2)

# Save and Load buttons
saveButton = ctk.CTkButton(root, text="Save", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=lambda: savePath(recordedActionList))
saveButton.grid(row=3, column=6)
loadButton = ctk.CTkButton(root, text="Load", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=loadPath)
loadButton.grid(row=3, column=7)

# Save Custom label
saveCustomLabel =  ctk.CTkLabel(root, text="Save Custom")
saveCustomLabel.grid(row=4,column=6, columnspan=2)

# Save Custom GUI
saveCustomButton = ctk.CTkButton(root, text="Save", width=60, height=10, fg_color=buttonColor, hover_color=buttonHoverColor, command=lambda: savePath(saveCustomInput.get()))
saveCustomButton.grid(row=5, column=6)
saveCustomInput = ctk.CTkEntry(root, width=80, height=10, border_color=entryBorderColor)
saveCustomInput.grid(row=5, column=7, padx=5)

# Seperator
functionSeperator = ctk.CTkFrame(master=root, height=1, width=1, corner_radius=0)
functionSeperator.grid(row=6, column=6, columnspan=2, sticky="ew", pady=10)

# Settings Label
settingsLabel =  ctk.CTkLabel(root, text="Settings")
settingsLabel.grid(row=7,column=6, columnspan=2)
themeSelect = ctk.CTkComboBox(root, width=60, height=10, border_color=entryBorderColor, button_color=entryBorderColor, command=changeTheme, values=("Light", "Dark"))
themeSelect.grid(row=8, column=6)
#---End of Row 3---


# Finishing stuff
root.mainloop()
listener.stop()
listener.join() # Wait for the listener to stop
mouseListener.stop()
mouseListener.join() # Wait for the listener to stop

# You can now process or save the recorded_keys list
print("\n--- Recorded Key Events ---")
for event in actionList:
    print(event)