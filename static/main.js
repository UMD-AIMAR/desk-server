function httpGet(theUrl) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, true );
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function updateQueue() {
    // Get queue data
    var queue = document.getElementById("queue");
    queue.textContent = httpGet("/api/queue");
    // setTimeout(updateQueue, 1000);
}

window.onload = function(e){
    // updateQueue();
}