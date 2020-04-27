# Files

    .
    ├── models            # skin lesion diagnosis models
    ├── datagen.py        # uses dataset.json to generate patient data
    ├── dataset.json      # stores a list of names, addresses, etc.
    ├── flaskaimar.db     # the actual database file (.db = database)
    ├── image_util.py     # handles patient images and skin diagnosis
    ├── patient_util.py   # patient-related functions (registration, queuing, etc.)
    └── routes.py         # handles incoming web requests, wrapper for all other functions

# Download
Make sure you have Python 3.7 installed. When installing, check the "Add Python to PATH" option.

On Mac, or Windows (if you have Git for Windows), run:
> git clone https://github.com/UMD-AIMAR/desk-server.git

Or go to the top, click 'Clone or download', and click 'Download ZIP'.

Open a Terminal and run:

> python -m pip install -r requirements.txt

# Running

Open a Terminal/Command Prompt, navigate to the folder 'desk-server', and run:
> python routes.py

When prompted for the Desktop IP, type "localhost" (without the quotes).

Then, go to `http://localhost:5000` in your browser. You should see a page with the text "AIMAR Homepage!"
That's it! You're now running a Flask server on your own computer.

# Description
AIMAR's architecture requires a central patient database and diagnosis system. The system runs on its own server (independent of any TurtleBot AIMAR units). Bots interact with the server by sending requests, e.g.

- "Give me patient X's info"
- "Update patient Y's zip code to 12345"
- "Run analysis on this skin lesion image"

From the bot, executing a diagnosis/database function (e.g. diagnosing a skin lesion) can be done with the Python requests library. An example code snippet would look like:

> skin_diagnosis_response = requests.post("https://desktop_ip/skin", data=skin_image_data)

Running a command like this in Python will send a request to the internet address 'desktop_ip'.
`desk-server` receives this request and handles it based on the endpoint specified (in this case, `/skin`).
routes.py is responsible for handling different endpoints - all the processing and logic is done in the other Python files.