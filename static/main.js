//
//
//
function httpASync(url, method, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var jsonObj = JSON.parse(this.responseText);
            if (callback) {
                callback(jsonObj);
            }
        }
    }
    xmlHttp.open(method, url, true);
    xmlHttp.send();
}

function updateDisplay() {
    var queue = document.getElementById("queue");
    httpASync("/api/queue", "GET", function(jsonObj) {
        queue.innerHTML = jsonObj.queue;
    });

    httpASync("/api/room/list", "GET", function(jsonObj) {
        updateTable(jsonObj);
    });
}

function updateDisplayRepeat() {
    updateDisplay();
    setTimeout(updateDisplayRepeat, 2000);
}

function updateTable(jsonObj) {
    var tbl = document.getElementById('room_table');
    tbl.innerHTML = ""
    var tbdy = document.createElement('tbody');

    var tr = document.createElement('tr');

    var pHeader = document.createElement('th');
    pHeader.innerHTML = "Patient ID";
    tr.appendChild(pHeader);
    var rHeader = document.createElement('th');
    rHeader.innerHTML = "Room #";
    tr.appendChild(rHeader);

    tbdy.appendChild(tr);

    for (var key in jsonObj) {
        var tr = document.createElement('tr');

        var patient = document.createElement('td');
        patient.innerHTML = key;
        tr.appendChild(patient);
        var room = document.createElement('td');
        room.innerHTML = jsonObj[key];
        tr.appendChild(room);

        tbdy.appendChild(tr);
    }
    tbl.appendChild(tbdy);
}

window.onload = function(e) {
    updateDisplayRepeat();

    var dequeuePatientButton = document.getElementById("dequeuePatient");
    dequeuePatientButton.addEventListener("click", function(event) {
        event.preventDefault();
        httpASync("/api/patient/dequeue", "POST");
        updateDisplay();
    });

    var enqueuePatientInput = document.getElementById("enqueuePatient");
    enqueuePatientInput.addEventListener("keydown", function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            httpASync("/api/patient/enqueue?patient_id=" + enqueuePatientInput.value, "POST");
            enqueuePatientInput.value = "";
            updateDisplay();
        }
    });

    var assignPatientInput = document.getElementById("assignPatient");
    assignPatientInput.addEventListener("keydown", function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            httpASync("/api/patient/assign?patient_id=" + assignPatientInput.value + "&room_number=" + assignRoomInput.value, "POST");
            assignPatientInput.value = "";
            assignRoomInput.value = "";
            updateDisplay();
        }
    });

    var assignRoomInput = document.getElementById("assignRoom");
    assignRoomInput.addEventListener("keydown", function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            httpASync("/api/patient/assign?patient_id=" + assignPatientInput.value + "&room_number=" + assignRoomInput.value, "POST");
            assignPatientInput.value = "";
            assignRoomInput.value = "";
            updateDisplay();
        }
    });

    var leaveRoomInput = document.getElementById("leaveRoom");
    leaveRoomInput.addEventListener("keydown", function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            httpASync("/api/patient/leave?patient_id=" + leaveRoomInput.value, "POST");
            leaveRoomInput.value = "";
            updateDisplay();
        }
    });
}