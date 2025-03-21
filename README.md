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

```
git clone https://github.com/Massiafz/Project.git
```

After you have git cloned the repository, you want to change directory into "Code":
```
cd .\Code
```

Then, navigate to the [`main.py`](main.py) file within the folder you cloned the repository into. Next, either click the "run" button in your IDE or enter the following command in the terminal:

```
python .\main.py
```


After doing this, the program will run and show up on your screen.


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
> *(Not yet started)* -> Plans include: CRUD operations on albums, searching, filtering, album images

### Iteration 3
> *(Not yet started)* -> Plans include: Personalized recommendations, song sample playback


## 📝 More Documentation 📝
To view more documentation, see [`Documentation`](Documentation/) and [`Planning`](Planning/).
Additionally, check out our [`BurnDownChart`](BurnDownChart.png) to examine our current pace for completing the software:
![BurnDownChart](https://github.com/user-attachments/assets/43336817-7d4b-4003-b31f-c5194fdf8405)


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



