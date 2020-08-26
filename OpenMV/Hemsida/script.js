const map_dimensions = [6, 6];
const car_coord = [0, 4];
let car_rotation = 0;
const clientID = "clientID_" + parseInt(Math.random() * 100);

window.onload = function() {
    var y_container = document.getElementById("map_container");
    for(y = map_dimensions[1]-1; y >= 0; y--){
        var new_y = '<div class="y_axis" id="' + y + '"></div>';
        y_container.innerHTML += new_y;
        for(x = 0; x < map_dimensions[0]; x++){
            var x_container = document.getElementById(this.y);  
            var coord = this.x + "," + this.y;
            var new_x = '<div class="box" " id="' + coord + '"><img style="" class="road_types" id="img' + coord + '" src="Images/PNG/missing.png"></div>';
            x_container.innerHTML += new_x;
        }
    }
}

function startConnect() {
    host = "maqiatto.com";                                  // Fetch the hostname/IP address and port number from the form
    port = 8883;
    username = "simon.ogaardjozic@abbindustrigymnasium.se";
    password = "scavenger";

    document.getElementById("messages").innerHTML += '<span>Connecting to: ' + host + ' on port: ' + port + '</span><br/>'; // Print output for the user in the messages div
    document.getElementById("messages").innerHTML += '<span>Using the following client value: ' + clientID + '</span><br/>';

    client = new Paho.MQTT.Client(host, Number(port), clientID);// Initialize new Paho client connection
    
    client.onConnectionLost = onConnectionLost; // Set callback handlers
    client.onMessageArrived = onMessageArrived;

    client.connect({
        userName : username, 
        password : password,
        onSuccess: onConnect,
        onFailure: onFail,
    });

    document.getElementById("Button").innerHTML = '<button onclick="startDisconnect()">Disconnect</button>'
}

function startDisconnect() {
    client.disconnect();
    document.getElementById("messages").innerHTML += '<span>Disconnected</span><br/>';
    document.getElementById("Button").innerHTML = '<button onclick="startConnect()">Connect</button>'
}

function onFail() {
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection to: ' + host + ' on port: ' + port + ' failed.</span><br/>'
}

function onConnect() {
    topic = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger"; 

    document.getElementById("messages").innerHTML += '<span>Subscribing to: ' + topic + '</span><br/>';

    client.subscribe(topic);
    
    init_order();
}

function onConnectionLost(responseObject) {
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection lost</span><br/>';
    if (responseObject.errorCode !== 0) {
        document.getElementById("messages").innerHTML += '<span>ERROR: ' + + responseObject.errorMessage + '</span><br/>';
    }
    document.getElementById("Button").innerHTML = '<button onclick="startConnect()">Connect</button>'
}

function init_order(){
    let order;
    order = new Paho.MQTT.Message('["A", 0]');
    order.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    client.send(order);
}

function pick_image(car_road){
    let images = [
        "Images/PNG/straight.png", 
        "Images/PNG/curve-left.png", 
        "Images/PNG/curve-right.png", 
        "Images/PNG/three-way-left.png", 
        "Images/PNG/three-way-right.png", 
        "Images/PNG/three-way.png", 
        "Images/PNG/four-way.png"
    ];

    let type_ = [
        [1, 0, 1, 0], 
        [0, 0, 1, 1],
        [0, 1, 1, 0], 
        [1, 0, 1, 1], 
        [1, 1, 1, 0], 
        [0, 1, 1, 1], 
        [1, 1, 1, 1]
    ];

    let img;
    for(j = 0; j <type_.length; j++){
        if(JSON.stringify(type_[j]) == JSON.stringify(car_road)) {
            img = images[j];
        }
    }

    return img;
}

function onMessageArrived(message) {
    console.log("onMessageArrived: " + message.payloadString);
    document.getElementById("messages").innerHTML += '<span>Topic: ' + message.destinationName + '  | ' + message.payloadString + '</span><br/>';
    if(message.payloadString.slice(-2) == ']]'){
        let car_object = get_json_data(message.payloadString);
        let car_road = car_object[1];
        let car_name = car_object[0];

        // the way u take, right left forward change car_roation

        car_rotation = 

        // place image
        let road_image = pick_image(car_road);
        
    }
}