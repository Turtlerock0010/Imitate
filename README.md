# Imitate
Welcome to Imitate! An autonomous path recorder and generator that can record and playback keystrokes and convert them into a ready to use auto!

![Imitate Logo](https://github.com/user-attachments/assets/72ef18ec-636d-4391-9960-bcfc6c282b52)

## WARNING (*Read Me First*)
Imitate **ACTIVELY** records keyboard and mouse inputs while open to function due to limitations in how I can incorperate libraries together. Although, Imitate **DOES NOT** save said keyboard or mouse inputs to **ANY** external storage. Everything Imitate saves is saved locally on your device and I am committed to keeping Imitate to not have any form of data collection to keep information safe and private.

## About
### What is Imitate?
Imitate is a program designed for miniFRC that can record keypresses and releases and replay keypresses. The program can also convert recordings into arduino to be used directly by the robot which supports keys with custom functionality tied to them.

### How was Imitate created?
Imitate initially started out as a recommendation from a team member in team 83 to make a program that can record and play back inputs. I then created the concept then expanded it to a full application, eventually becoming a full application. I drew GUI inspiration from Natro Macro, a macro for Bee Swarm Simulator.

### What drive trains does Imitate allow conversion to?
Imitate has a limited amount of drive trains that are supported, with further plans to expand to more drive trains in the future. Currently, there are 3 drive trains supported:
- Tank
- Mecanum
- Fortnite

## Setup
1. Download your OS specific version of Imitate from releases in the GitHub
2. Allow Imitate through your OS security
3. Enjoy making autos!

NOTE: *Imitate is unable to be tested on linux by Turtlerock0010, and is unverified if the files work*

## User Manual
<img width="592" alt="Imitate as of July 2, 2025." src="https://github.com/user-attachments/assets/2367f862-465a-4d40-b856-8eb96bb76d40" />

### Action Section

#### Start Recording
Press the `Start` button next to the `Record` label to start recording inputs.

#### End Recording
To stop recording, press the `Stop` button in the same place as the `Start` button to stop the recording. Which saves the path to memory for use.

#### Play Recording
Press the `Play` button next to the, `Play` label to play the recording in memory. Before execution of the recording a **5** second delay is given to allow the user to refocus the computer to another window.

#### Copy Recording
Once a recording is in memory, the recording is then presented on the entry box which can be copied using the `Copy` button

#### Replay Recording
Using the entry box next to the `Replay` button, you can input a recording compatibile to Imitate and plays the recording and saves the recording to memory.

#### Mouse Refocus
Press the `Set` button next to the entry box to set the location where your mouse will click to refocus to a different application. The location of the next click after clicking the `Set` button will be the location saved where the location will appear on the entry box where the mouse location will then be used for refocusing when `play` is pressed.

### Function Section

#### Function Name Input
Using the entry box next to the `Name:` label, you can input a name for the function to be created. NOTE: *Imitate will remove special characters to adhere to arduino syntax.*

#### Custom Functionality Creation
Press the `Add` button to add custom functionality to a key when read by giving a key to the first smaller box then whatever code you desire for the second longer box.

#### Remove Custom Functionality
By selecting a letter from the list in the combo box and pressing the `Remove:` button, the letter and its functionality will be removed.

#### Drive Train Input
To select a drive train, next to the `Drvtrain` label, select a drive train in the combo box. NOTE: *A drive train is required to sucessfully create a function*

#### Create Function
When the `Create Function` button is pressed, Imitate translates the recording in memory into executable code for Arduino. NOTE: *A drive train is required and if the name entry box is left blank the name will default to "myPath"*

#### Copy Function
When a function has been created, pressing the `Copy` button will copy the function inside the text box next to it into your clipboard.

### Data Section

#### Save Recording
Press the `Save` button to prompt a save dialog to save the path in memory to a .txt file. NOTE: **Imitate will only save the path, not the application refocus mouse location**

#### Load Recording
Press the `Load` button to prompt a load dialog to load in a .txt file into memory. NOTE: *Imitate will reject invalid files.*

#### Save Custom Recording
Pressing the `Save` button next to the entry box will save the recording to a .txt file.
