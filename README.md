![](https://github.com/cem-yilmaz/GCSearch/blob/cems-features/frontend/GCSearch/public/assets/GCSearch%20Logo%20(white).cropped.png)
# 🔍 GCSearch - A Modern Search Engine 🖥️ that runs locally (offline) 🔌 on your exported data 💾
GCSearch intelligently formats your raw data exports from your favourite messaging apps, and allows you to search through **all** of them, returning the most relevant results. All data and processing is performed _locally_, meaning you can safely browse your own data at your own leisure.

GCSearch is powered by a robust ⚗️ Flask backend, and brought to life with a custom-built bespoke ⚛️ React frontend.

GCSearch was created for **The University of Edinburgh's** "_Text Technologies for Data Science_" (TTDS) course in 2025, and was the collaborative effort of Cem, Ray, Layla, Yu-Shin, and Efe. Please see [Credits](#Credits) for further details.
## Supported Messaging Platforms
- **Instagram**
- **WhatsApp**
- **WeChat**
- **LINE**
# Requirements
- Python >=3.10.12
- NodeJS
# Setup
First, clone this repository (repo) locally.
## Installing required files
### Python
In a terminal, navigate to where you cloned the repo, and install the `requirements.txt` file.

**We strongly reccomend creating a virtual environment (`.venv`). You may have to install the VirtualEnv package if you do not already have it on your system (`pip install virtualenv`)**.
```
python3 -m venv .venv
```
Then activate this environment so you can install packages directly to it.
On **Windows**, this can be done with the following command:
```
.\.venv\Scripts\Activate.ps1
```
On **MacOS/Linux**, this can be done with the following command:
```
source \.venv\bin\activate
```

You should see a little `(.venv)` next to your terminal prompt. You can now run:
```
pip install -r requirements.txt
```
### NodeJS
Once you have NodeJS installed, navigate to where you cloned the repo. Then, navigate into `frontend/GCSearch`, and run 
```
npm install
```
## Getting and processing the data
Follow the respective guides for [exporting your own data](https://github.com/cem-yilmaz/GCSearch/wiki#how-to-export-your-data-from-the-supported-apps).
Place these exports inside of `backend/core/export/[instagram][whatsapp][wechat][line]`, depending on which platform you got these from.

(TODO: make a script to assist with creation of `csv` chatlogs and PIIs)
# Running
Once you have installed the prerequisite files, and downloaded and parsed your data, open up two terminals.
**It is recommended to start the server _first_ to avoid any syncing issues**.
## Backend Server
The backend server manages all the internal search engine operations. Navigate to `backend/` and run
```
python3 server.py
```
This should start the server on port `5000`. This is where the frontend will expect results from, so if this isn't the case, check your ports (or change the frontend code **if you know what you are doing!**)
## Frontend Interface
The frontend handles the actual interface for viewing the chats. Navigate to `frontend/GCSearch` and run
```
npm run dev
```
This should start the interface on [localhost:5174](http://localhost:5174/). Naviagate to this to start searching!
# Credits
todo
