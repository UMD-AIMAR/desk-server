# desk-server
Running on central computer, handles diagnosis and database

# Running
> python routes.py

# Description
AIMAR's architecture requires a central patient database and diagnosis system. The system runs on its own server (independent of any TurtleBot AIMAR units). Bots interact with the server by sending requests, e.g.

- "Give me patient X's info"
- "Update patient Y's zip code to 12345"
- "Run analysis on this skin lesion image"

From the bot, executing a diagnosis/database function (e.g. diagnosing a skin lesion) can be done with the Python requests library. An example code snippet would look like:

> skin_diagnosis_response = requests.post("https://desktop_ip/skin", data=skin_image_data)

In routes.py there is a Python function that executes when the user visits this URL. Notice how routes.py doesn't contain any references to sqlite3 (database library) or keras (deep learning library). It instead imports functions from db and skin, where db.py and skin.py are the scripts that encapsulate the database and skin image processing functions, respectively.
