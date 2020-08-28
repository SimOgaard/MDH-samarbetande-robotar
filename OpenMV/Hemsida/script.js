const mapDimensions = [6, 6];
const clientID = "clientID_" + parseInt(Math.random() * 100);

window.onload = function() {

    // let containerMaps = document.getElementById("maps"); 

    // // g = document.createElement('div');
    // // g.setAttribute("id", "Div1");
    // let containerMap = containerMaps.createElement('div');
    // containerMap.setAttribute("id", "sharedMapContainer");

    // // let containerMap = document.getElementById("sharedMapContainer");
    // let coordY = mapDimensions[1]-1;
    // let coordX = 0;
    // do {
    //     coordX = 0;

    //     let containerY = '<div class="axisY" id="' + coordY + '"></div>';
    //     containerMap.innerHTML += containerY;
        
    //     do {
    //         let containerY = document.getElementById(coordY);
    //         let coordXY = coordX + "," + coordY;
    //         let containerX = '<div class="box" " id="' + coordXY + '"><img style="" class="road_types" id="img' + coordXY + '" src="Images/PNG/missing.png"></div>';
    //         containerY.innerHTML += containerX;

    //         coordX++;
    //     }while(coordX < mapDimensions[0]);
    //     coordY--;
    // }while(coordY >= 0);

    const createMap = function(mapDimensions, id, containerMaps = document.getElementById("mapsContainer")){
        containerMaps.innerHTML += `<div id="map${id}"></div>`;
        let containerMap = document.getElementById(`map${id}`);

        console.log(containerMap)

        let coordY = mapDimensions[1]-1;
        let coordX = null;
        do {
            coordX = 0;

            let containerY = `<div class="axisY" id="${id}:${coordY}"></div>`;
            containerMap.innerHTML += containerY;
            
            do {
                let containerY = document.getElementById(`${id}:${coordY}`);
                // let coordXY = coordX + "," + coordY; 
                let containerX = `<div class="box" id=${id}:${coordX},${coordY}"><img class="road_types" id="img${coordX},${coordY}" src="Images/PNG/missing.png"></div>`;
                containerY.innerHTML += containerX;

                coordX++;
            }while(coordX < mapDimensions[0]);
            coordY--;
        }while(coordY >= 0);
    }

    // const createIndividualMap = function(object){

    // }
    let mapDimensionsExtended = [mapDimensions[0]*2+1, mapDimensions[1]*2+1]
    createMap(mapDimensions, "Shared")
    createMap(mapDimensionsExtended, "S")
    createMap(mapDimensionsExtended, "K")

    // cars.forEach(createMap);
    
    // individual maps for each car aswell
}

const startDisconnect = function() {
    client.disconnect();
    document.getElementById("messages").innerHTML += '<span>Disconnected</span><br/>';
    document.getElementById("Button").innerHTML = '<button onclick="startConnect()">Connect</button>'
}

const onFail = function() {
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection to: ' + host + ' on port: ' + port + ' failed.</span><br/>'
}

const initOrder = function(){
    let order;
    order = new Paho.MQTT.Message('["A", 0]');
    order.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    client.send(order);
}

const onConnect = function() {
    topic = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger"; 

    document.getElementById("messages").innerHTML += '<span>Subscribing to: ' + topic + '</span><br/>';

    client.subscribe(topic);
    
    initOrder();
}

const onConnectionLost = function(responseObject) {
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection lost</span><br/>';
    if (responseObject.errorCode !== 0) {
        document.getElementById("messages").innerHTML += '<span>ERROR: ' + + responseObject.errorMessage + '</span><br/>';
    }
    document.getElementById("Button").innerHTML = '<button onclick="startConnect()">Connect</button>'
}

const startConnect = function() {
    const host = "maqiatto.com";                                  // Fetch the hostname/IP address and port number from the form
    const port = 8883;
    const username = "simon.ogaardjozic@abbindustrigymnasium.se";
    const password = "scavenger";

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

// ha de två individuella mapparna brevid varandra, starta imitten 
// och utgå från de när du uppdaterar mappen

// på nya anrop från serven eller från bilarna "try fitting the two maps together"

let cars = [
    Simon = {
        // map:
        name: "S",
        recentOrder: 0,
        coord: [0, 0], // start cordinat är math.top(mapDimensionsExtended/2)
        rotation: 0,
        gotData: function(data){
            console.log(data)
            // this.rotation, this.recentOrder and this.coord to update map and coords
            // @ new this.carCoords place data[1]
            // använd this.rotation för att veta om nya cords är [x+1,y] eller [x,y+1]
            // data[1] is the previous map aka [1,1,1,1] and this.carCoords 
        },
        chooseOrder: function(){
            return [0,1,2];
        },
        order: function(order = chooseOrder()){
            let orderMessage = new Paho.MQTT.Message(`["S", ${order}]`);
            orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
            client.send(orderMessage);
            this.recentOrder = order;
        }
    },
    // Khe = {
    //     carCoord: [5, 5],
    //     carRotation: 0
    // }
]

const getJsonData = function(JSON_DATA){
    const road_probability = 0.65
    const JSON_array = JSON.parse(JSON_DATA);
    const JSON_road_type = JSON_array[1];
    let road_array = [];
    
    for(i = 0; i < JSON_road_type.length; i++) {
        const probability = JSON_road_type[i]/JSON_road_type[2];
        if (probability >= road_probability){
            road_array.push(1);           
        }else{
            road_array.push(0);
        }
    }

    return [JSON_array[0], road_array];
}

const onMessageArrived = function(){
    document.getElementById("messages").innerHTML += '<span>Topic: ' + message.destinationName + '  | ' + message.payloadString + '</span><br/>';

    jsonObject = getJsonData(message.payloadString);

    const directThis = function(object){
        if (jsonObject[0] === object.name){
            object.gotData(jsonObject);
            break;
        }
    }

    cars.forEach(directThis);
}

//  create car objects with values and functions
// function initOrder(){
    
// }