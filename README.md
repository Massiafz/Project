# Sahar's Music Cataloging Software 🎵💿🎧

### Developed By BrightByte:
- **Project Manager:** Bach Nguyen (100926453)
- **Technical Manager:** Massi Afzal (100911029)
- **Software Quality Lead:** Moksh Patel (100916422)
- **Back-End Lead:** Jason Guan (100927182)
- **Front-End Lead:** Vincent Tseng (100912590)

## 📃 Table Of Contents 📃
- **[Introduction](#-introduction-)**
- **[Instructions To Run](#-instructions-to-run-)**
- **[Iterations](#-iterations-)**
    - [Iteration 1](#iteration-1)
    - [Iteration 2](#iteration-2)
    - [Iteration 3](#iteration-3)
- **[More Documentation](#-more-documentation-)**


## 🎶 Introduction 🎶
This is a music cataloging software that allows users to add, delete, and edit albums within the catalog.
At first, users will be guided to sign up for an account if it is their first time using the program.
Else, they will be able to login with their username/email and password.
Once they are logged in, they will be able to access the main cataloging features mentioned before.


## ❓ Instructions To Run ❓
To retrieve the program, first ensure git is installed on the computer you are using, then clone this GitHub repository inside a terminal with the command below:

### Step 1: Clone the Repository

Open your terminal or command prompt and run the following command:
```bash
git clone https://github.com/Massiafz/Project.git
```

### Step 2: Navigate to the Code Directory

Change your directory to where the application code is located:
```bash
cd Project
```

### Step 3: Run the Executable

- **For Mac/Linux Users:**
  ```bash
  ./brightbyte-linux
  ```
- **For Windows Users:**
  ```batch
  ./brightbyte-windows
  ```
  Windows and Linux are able to run the executable from the file explorer but mac is not able to.

*These scripts will set up and launch the application on your system.*



## 👟 Iterations 👟

### Iteration 1

#### Demo Phase2 Video:
https://youtu.be/6iMuDX0EgMA

#### Overview
In our first iteration, we created the main account functionalities within the program including:
- Create account
- Log in to account
- Edit account
- Delete account

With these account features, we designed the UI for logging in, signing up, and editing your account.
Moreover, the csv file containing the album data loads automatically to the catalog screen once logged in.
Users can then do the following:
- Add album
- Edit album
- Delete album

#### What Went Well
During this iteration, we practiced agile development very well, and our collaboration was great which led to consistent planning and progress throughout each user story. We were able to achieve this by providing timely and detailed updates on progress and any difficulties that may have arose. This ensured that we would stay on track, and to pick up the pace if we were behind scehdule during the iteration.
Additionally, we were able to utilize our kanban board effectively to stay organized and to know what immediate and following tasks and user stories to work on.
Furthermore, even though we had some difficulty implementing specific requirements, we were able to complete them all in the end.

#### What Can Be Improved
One of the parts we can improve for the software would be the UI/UX design.
We will do this once you confirm the preferred colour scheme for the program.

#### Challenges And Ways To Address Them
A challenge we are facing is figuring out how to prepare and add the album images for [`Iteration 2`](#iteration-2).
Some ways to address this would be to either download the album images individually or to use an API for efficiency.

### Iteration 2
- Worked on the following tasks...
- Adding Images for album covers
- Final changed to CSV (after editing, adding, or deleting)
- Searching for songs
- Guest Account
- Database/Build
- Multi-threading
- UI Updates

### Iteration 3
- Favourites Section
- Songs for each album
- Access rights


## 📝 More Documentation 📝
To view more documentation, see [`Documentation`](Documentation/) and [`Planning`](Planning/).
Additionally, check out our [`BurnDownChart`](BurnDownChart.png) to examine our current pace for completing the software:
![BurnDownChart](https://github.com/user-attachments/assets/7a0906c8-b240-4903-a6f6-19b7b3cb4aa7)





# Project Setup Guide

## Overview
This project automates data processing and analysis using Python. The provided `Makefile` simplifies installation, execution, and cleanup.

## Prerequisites
- Python 3 installed
- `pip` installed
- Required Python packages (listed in `requirements.txt`)

## Installation & Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/Massiafz/Project.git
   cd Project
   ```
2. Install dependencies:
   ```sh
   make install
   ```

## Running the Project
1. Process the data:
   ```sh
   make process
   ```
2. Run the main script for analysis/plotting:
   ```sh
   make plot
   ```

## Running Tests
(Currently, no test target is defined in the Makefile. If tests exist, a `make test` command should be added.)

## Cleaning Up
To remove temporary files:
```sh
make clean
```
You will be prompted for confirmation before deletion.

## Additional Notes
- Ensure all required data files (e.g., `data.csv`) are available in the correct directories before running.
- If running on Windows, you may need to use `python` instead of `python3` and `pip` instead of `pip3`.

For deployment instructions, additional setup may be required.



