#-----------------------Library Init-----------------------
from fileinput import filename
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
import json

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
stateList = []
resultFunction = ""

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
            if recording:
                writeToOperationTerminal(f"Key pressed: {key_char}")
    else:
        actionList.append(('pressed', key_char, time.time()))
        if recording:
            writeToOperationTerminal(f"Key pressed: {key_char}")


def on_release(key):
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)

    actionList.append(('released', key_char, time.time()))
    if recording:
            writeToOperationTerminal(f"Key released: {key_char}")

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
            writeToOperationTerminal("Recorded Mouse Click at: " + str(recordedClick[0]) + " with button: " + recordedClick[1])
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
        writeToSaveTerminal("Path saved to: " + file.name)

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
    userInput = functionNameInput.get()
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


    writeToFunctionOutput(resultFunction)


def copyFunction():
    print(resultFunction)
    root.clipboard_clear()
    root.clipboard_append(str(resultFunction))


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
    stateList.append(("mode", color))


def on_closing():
    saveState()
    root.destroy()


def switch_view(value):
    # Bring the selected frame to the front
    frame = frames[value]
    frame.tkraise()


def writeToOperationTerminal(text):
    operationTerminal.insert("end", "\n" + "> " + text)
    operationTerminal.see("end") # Scroll to the end


def writeToFunctionOutput(text):
    functionOutput.insert("end", "\n" + "> " + text)
    functionOutput.see("end") # Scroll to the end


def writeToSaveTerminal(text):
    saveTerminal.insert("end", "\n" + "> " + text)
    saveTerminal.see("end") # Scroll to the end


def clear_focus(event):
    root.focus()


def loadState():
    # Create Data Dictionary
    data = {}

    # Load Data from state.json
    try:
        with open(stateFile, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        messagebox.showinfo("Error", "state.json file not found.")
    except json.JSONDecodeError:
       messagebox.showinfo("Error", "Unable to parse through state.json.")
    

    # Load Data into program

    # Set theme
    ctk.set_appearance_mode(data["Theme"])
    themeSelect.set(data["Theme"].capitalize())


def saveState():
    # Create Data Dictionary
    data = {}

    # Load Data from state.json
    try:
        with open(stateFile, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        messagebox.showinfo("Error", "state.json file not found.")
    except json.JSONDecodeError:
       messagebox.showinfo("Error", "Unable to parse through state.json.")
    
    # Update Data
    data["Theme"] = ctk.get_appearance_mode()

    # Dump Data
    with open(stateFile, 'w') as file:
        json.dump(data, file, indent=4)





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

# Closing Setup
root.protocol("WM_DELETE_WINDOW", on_closing)

# Icon Setup
image_path = resourcePath(os.path.join("assets", "Imitate Logo.png"))
load = Image.open(image_path)
render = ImageTk.PhotoImage(load)
root.iconphoto(False, render)

# Grid Config
root.grid_rowconfigure(1, weight=1) # Content expands
root.grid_columnconfigure(0, weight=1)

# State Saving
stateFile = resourcePath(os.path.join("assets", "state.json"))

# Appearances
imitateThemePath = resourcePath(os.path.join("assets", "imitateTheme.json"))
ctk.set_default_color_theme(imitateThemePath)
ctk.set_appearance_mode("dark")


buttonColor = "#2e6eeb"
buttonHoverColor = "#275BBF"
entryBorderColor = "#4B7EC8"

# Overall Layout
nav_frame = ctk.CTkFrame(root, height=50, corner_radius=0)
nav_frame.grid(row=0, column=0, sticky="ew")

menu_options = ["Actions", "Functions", "Data", "Settings"]
seg_button = ctk.CTkSegmentedButton(nav_frame, 
                                    values=menu_options,
                                    command=switch_view,
                                    corner_radius=10,
                                    selected_color=buttonColor,
                                    selected_hover_color=buttonHoverColor,
                                    unselected_color="#648AC2",
                                    unselected_hover_color="#4B7BC4",
                                    text_color="#FFFFFF",
                                    fg_color="#648AC2",
                                    height=30
                                    )
seg_button.pack(pady=5, padx=20)
seg_button.set(menu_options[0]) # Set the default view

# Content Container
container = ctk.CTkFrame(root, fg_color="transparent")
container.grid(row=1, column=0, sticky="nsew")

# Frame Creation
frames = {}



# ----- Actions -----
frames[menu_options[0]] = ctk.CTkFrame(container, fg_color="transparent")

# -- Action Container --
actionContainer = ctk.CTkFrame(frames[menu_options[0]], 
                          width=150, 
                          height=210,
                          border_width=1
                          )
actionContainer.grid(row=0, column=0, padx=10, pady=10)
actionContainer.grid_propagate(False)

recordingButton = ctk.CTkButton(actionContainer, 
                                    text="Record",  
                                    height=30, 
                                    width=130,
                                    command=record
                                    )
recordingButton.grid(row=0, column=0, padx=(10,10), pady=(10,0), sticky="ew")

playButton = ctk.CTkButton(actionContainer, 
                                text="Play", 
                                height=30, 
                                width=130,
                                command=lambda: threadManager("playRecording")
                                )
playButton.grid(row=1, column=0, padx=(10,10), pady=(10,0), sticky="ew")

Separator = ctk.CTkFrame(actionContainer, 
                                height=1, 
                                fg_color="#4B7EC8", 
                                width=130
                                )
Separator.grid(row=2, column=0, padx=10, pady=(10,0), sticky="ew")

mouseFocusButton = ctk.CTkButton(actionContainer, 
                                        text="Set Focus", 
                                        height=30, 
                                        width=130,
                                        command=lambda: startRecordingMouse()
                                        )
mouseFocusButton.grid(row=3, column=0, padx=(10,10), pady=(10,0), sticky="ew")

Separator2 = ctk.CTkFrame(actionContainer, 
                                height=1, 
                                fg_color="#4B7EC8", 
                                width=130
                                )
Separator2.grid(row=4, column=0, padx=10, pady=(10,0), sticky="ew")

replayButton = ctk.CTkButton(actionContainer, 
                                        text="Replay", 
                                        height=30, 
                                        width=50,
                                        command=lambda: threadManager("replayRecording")
                                        )
replayButton.grid(row=5, column=0, padx=(10,10), pady=(10,0), sticky="w")

replayInput = ctk.CTkEntry(actionContainer, 
                                placeholder_text="Enter Replay Script", 
                                width=70, 
                                height=30, 
                                border_width=2
                                )
replayInput.grid(row=5, column=0, padx=(10,10), pady=(10,0), sticky="e")
# -- End of Action Container --


operationTerminal = ctk.CTkTextbox(frames[menu_options[0]], 
                                        width=300, 
                                        height=170, 
                                        border_width=1, 
                                        )
operationTerminal.grid(row=0, column=1, padx=(0,10), pady=10, sticky="n")
operationTerminal.insert("0.0", "> Operation Terminal...")

copyActionsButton = ctk.CTkButton(frames[menu_options[0]], 
                                        text="Copy Actions", 
                                        height=30, 
                                        width=100,
                                        command=copyActions
                                        )
copyActionsButton.grid(row=0, column=1, padx=(0,10), pady=(0,10), sticky="sw")

actionsBox = ctk.CTkEntry(frames[menu_options[0]], 
                                        placeholder_text="Copy Actions Here...", 
                                        width=190, 
                                        height=30, 
                                        border_width=2
                                        )
actionsBox.grid(row=0, column=1, padx=(0,10), pady=(0,10), sticky="se")
#----- End of Actions -----



#----- Functions -----
frames[menu_options[1]] = ctk.CTkFrame(container, fg_color="transparent")

functionNameInput = ctk.CTkEntry(frames[menu_options[1]],
                                        placeholder_text="Function Name...",
                                        width=150,
                                        height=30,
                                        border_width=2
                                        )
functionNameInput.grid(column=0, row=0, padx=10, pady=(10,0))


#----- Function List -----
functionContainer = ctk.CTkFrame(frames[menu_options[1]],
                                width=150,
                                height=170,
                                border_width=1
                                )
functionContainer.grid(column=0, row=1, padx=10, pady=10)
functionContainer.grid_propagate(False)

customKeyInput = ctk.CTkEntry(functionContainer, 
                                width=30, 
                                height=30, 
                                border_width=2
                                )
customKeyInput.grid(row=0, column=0, padx=(10,10), pady=(10,0), sticky="n")

customActionInput = ctk.CTkEntry(functionContainer,
                                width=45, 
                                height=30, 
                                border_width=2
                                )
customActionInput.grid(row=0, column=0, padx=(10,10), pady=(10,0), sticky="e")

addActionButton = ctk.CTkButton(functionContainer,
                                text="Add",
                                height=30,
                                width=45,
                                command=addKeyStroke
                                )
addActionButton.grid(row=0, column=0, padx=(10,10), pady=(10,0), sticky="w")

removeActionButton = ctk.CTkButton(functionContainer,
                                text="Remove",
                                height=30,
                                width=45,
                                command=removeKeyStroke
                                )
removeActionButton.grid(row=1, column=0, padx=(10,10), pady=(10,0), sticky="w")

removeActionSelect = ctk.CTkComboBox(functionContainer,
                                values=" ",
                                width=65,
                                height=30,
                                border_width=2
                                )
removeActionSelect.grid(row=1, column=0, padx=(10,10), pady=(10,0), sticky="e")

driveTrainInput = ctk.CTkComboBox(functionContainer,
                                values=validDriveTrains,
                                width=130,
                                height=30,
                                border_width=2
                                )
driveTrainInput.grid(row=2, column=0, padx=(10,10), pady=(10,0), sticky="ew")
#-----End of Function List -----


functionOutput = ctk.CTkTextbox(frames[menu_options[1]],
                                    width=300,
                                    height=170,
                                    border_width=1,
                                    )
functionOutput.grid(column=1, row=0, rowspan=2, padx=(0,10), pady=10, sticky="n")
functionOutput.insert("0.0", "> Function Output...")

generateFunctionButton = ctk.CTkButton(frames[menu_options[1]],
                                            text="Generate Function </>",
                                            height=30,
                                            width=190,
                                            command=lambda: threadManager("createFunction")
                                            )
generateFunctionButton.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="ws")

copyFunctionButton = ctk.CTkButton(frames[menu_options[1]],
                                            text="Copy Function",
                                            height=30,
                                            width=100,
                                            command=copyFunction
                                            )
copyFunctionButton.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="es")
#----- End of Functions -----




#----- Data -----
frames[menu_options[2]] = ctk.CTkFrame(container, fg_color="transparent")


#----- Data List -----
dataList = ctk.CTkFrame(frames[menu_options[2]],
                                width=150,
                                height=210,
                                border_width=1
                                )
dataList.grid(column=0, row=1, padx=10, pady=10)
dataList.grid_propagate(False)

saveButton = ctk.CTkButton(dataList,
                                    text="Save",
                                    height=30,
                                    width=130,
                                    command=lambda: savePath(recordedActionList)
                                    )
saveButton.grid(row=0, column=0, padx=(10,10), pady=(10,0), sticky="ew")

loadButton = ctk.CTkButton(dataList,
                                    text="Load",
                                    height=30,
                                    width=130,
                                    command=loadPath
                                    )
loadButton.grid(row=1, column=0, padx=(10,10), pady=(10,0), sticky="ew")
#----- End of Data List -----


saveTerminal = ctk.CTkTextbox(frames[menu_options[2]],
                                    width=300,
                                    height=170,
                                    border_width=1
                                    )
saveTerminal.grid(column=1, row=0, rowspan=2, padx=(0,10), pady=10, sticky="n")
saveTerminal.insert("0.0", "> Data Output...")

saveCustomButton = ctk.CTkButton(frames[menu_options[2]],
                                            text="Save Custom Data",
                                            height=30,
                                            width=100,
                                            command=lambda: savePath(saveCustomInput.get())
                                            )
saveCustomButton.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="ws")

saveCustomInput = ctk.CTkEntry(frames[menu_options[2]],
                                placeholder_text="Custom Input...",
                                width=165,
                                height=30,
                                border_width=2,
                                )
saveCustomInput.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="es")
#----- End of Data -----



#----- Settings -----
frames[menu_options[3]] = ctk.CTkFrame(container, fg_color="transparent")


# -- Settings Container --
settingsContainer = ctk.CTkFrame(frames[menu_options[3]], 
                          width=150, 
                          height=210,
                          border_width=1
                          )
settingsContainer.grid(row=0, column=0, padx=10, pady=10)
settingsContainer.grid_propagate(False)

themeSelect = ctk.CTkComboBox(settingsContainer,
                                values=("Light", "Dark"),
                                width=130,
                                height=30,
                                border_width=2,
                                command=changeTheme
                                )
themeSelect.grid(row=0, column=0, padx=(10,10), pady=(10,0), sticky="ew")
# -- End of Settings Container --


# -- Credits Container --
creditsBox = ctk.CTkFrame(frames[menu_options[3]],
                                    width=300,
                                    height=210,
                                    border_width=1,
                                    )
creditsBox.grid(column=1, row=0, rowspan=2, padx=(0,10), pady=10, sticky="n")
creditsBox.grid_propagate(False)

creditsLabel = ctk.CTkLabel(creditsBox,
                                text="Created by The Pink Fluffy Unicorns [83]\nProject Lead: Turtlerock0010\n\n Special Thanks to:\n- The Pink Fluffy Unicorns [83]\n- Testers\n- Stargazers\n- And Most importantly: \n   You for using this software!\n\n Licensed under GNU GPL v3.0 \n Made with ❤️ by Turtlerock0010",
                                justify="left",
                                )
creditsLabel.grid(column=0, row=0, padx=10, pady=10, sticky="w")
# -- End of Credits Container --
#----- End of Settings -----

for frame in frames.values():
    frame.grid(row=0, column=0, sticky="nsew")

switch_view(menu_options[0])

loadState()

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