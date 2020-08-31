// Universal constants
const mapDimensions = [6, 6];
const mapDimensionsExtended = [mapDimensions[0]*2-1, mapDimensions[1]*2-1];
const clientID = "clientID_" + parseInt(Math.random() * 100);

const arrayCorespondingImage = {
    straight: [1, 0, 1, 0],
    curve_left: [0, 0, 1, 1],
    curve_right: [0, 1, 1, 0],
    three_way_left: [1, 0, 1, 1],
    three_way_right: [1, 1, 1, 0],
    three_way: [0, 1, 1, 1],
    four_way: [1, 1, 1, 1]
}

// Universal calculation functions
let mapSkeletonS = [];
let mapSkeletonK = [];
for(let y=mapDimensionsExtended[1]-1; y>=0; y--) {
    mapSkeletonS[y] = [];
    mapSkeletonK[y] = [];
    for(var x=0; x<mapDimensionsExtended[0]; x++) {
        mapSkeletonS[y][x] = [null, null];
        mapSkeletonK[y][x] = [null, null];
    }
}

const arrayRotate = function(roadArray, rotation) {
    for (let i = 0; i < roadArray.length; i++) {
        if (rotation < 0){
            roadArray.unshift(roadArray.pop());
        } else{
            roadArray.push(roadArray.shift());
        } 
    }
    return roadArray;
}

const arraysMatch = function(arr1, arr2) {
    console.log(arr1, arr2)
	if (arr1.length !== arr2.length){ 
        return false;
    }
	for (var i = 0; i < arr1.length; i++) {
		if (arr1[i] !== arr2[i]) {
            return false;
        }
	}
	return true;
};
  
const returnImageDirOfArray = function(roadArray){
    for (const key in arrayCorespondingImage){
        if (arraysMatch(roadArray, arrayCorespondingImage[key])) {
            console.log(arrayCorespondingImage[key], key)
            return `Images/PNG/${key}.png`;
        }
    }
}

// Cars
let cars = [
    Simon = {
        name: "S",

        carCoord: [mapDimensions[0]-1, mapDimensions[1]-1],
        viewCoord: [mapDimensions[0]-1, mapDimensions[1]],
        rotation: 0,

        map: mapSkeletonS,

        recentOrder: 0,

        // functions that calculate stuff
        carAct: function(roadArray){

            console.log(this.carCoord);
            console.log(this.viewCoord);
            console.log(this.rotation);
            console.log(this.recentOrder);
            console.log(roadArray);
            console.log(this.map);

            if (this.recentOrder === 1 || arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
                this.rotation+=90;
            } else if (this.recentOrder === 2 || arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
                this.rotation-=90;
            }

            this.carCoord = [this.viewCoord[0],this.viewCoord[1]];
            this.map[this.carCoord[0]][this.carCoord[1]][0] = [...roadArray];

            console.log("AAAAAAA");
            console.log(Math.sin(0))
            console.log(this.rotation*Math.PI/180)
            console.log(Math.sin(this.rotation*Math.PI/180))
            console.log(Math.cos(this.rotation*Math.PI/180))

            this.viewCoord[0] = this.viewCoord[0]+Math.round(Math.sin(this.rotation*Math.PI/180))
            this.viewCoord[1] = this.viewCoord[1]+Math.round(Math.cos(this.rotation*Math.PI/180))

            console.log(this.carCoord);
            console.log(this.viewCoord);
            console.log(this.rotation);
            console.log(this.recentOrder);
            console.log(roadArray);
            console.log(this.map);

            this.updateMapHTML(roadArray)

        },
        
        getCarOrder: function(){

        },
        orderCar: function(order){
            let orderMessage = new Paho.MQTT.Message(`[${this.name}, ${order}]`);
            orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
            client.send(orderMessage);
        },
        
        // functions that change html
        carInOrigoHTML: function(){
            const carOrigoContainer = document.getElementById(`${this.name}:${this.carCoord[0]},${this.carCoord[0]}`);
            carOrigoContainer.classList.add(`imgCar`);
        },
        messagesCarHTML: function(message, msgFromCar){
            let className = null;
            if (msgFromCar){
                className = `.car${this.name}Sent`;
            } else {
                className = `.car${this.name}Received`;
            }
            const containerForMessages = document.querySelector(className);
            containerForMessages.innerHTML += message;
        },
        updateMapHTML: function(roadArray){
            imageDir = returnImageDirOfArray(roadArray);
            console.log(imageDir, this.carCoord)
            const imageElement = document.getElementById(`${this.name}:${this.carCoord[0]},${this.carCoord[1]}`);
            imageElement.src = imageDir;
        }
    }
]

// Html Init
const createMap = function(mapDimensions, id){
    const containerForMap = document.querySelector(`.carMap${id}`);

    for (let y = mapDimensions[1]-1; y >= 0; y--) {
        containerForMap.innerHTML += `<div class="axisY" id="${id}:${y}"></div>`;
        
        for (let x = 0; x < mapDimensions[0]; x++) {
            const containerY = document.getElementById(`${id}:${y}`);
            containerY.innerHTML += `<img class="roadImage" id="${id}:${x},${y}" src="Images/PNG/missing.png">`;
        }
    }
}

createMap(mapDimensions,"Both");
cars.forEach(car=>{
    createMap(mapDimensionsExtended, car.name);
    car.carInOrigoHTML();
})

// MQTT

const buttonChange = function(connectLost){
    const button = document.querySelector(".connectButton");

    if (connectLost){
        button.innerHTML = '<button onclick="startConnect()" id="notConnected">Connect</button>'
    } else {
        button.innerHTML = '<button onclick="startDisconnect()" id="isConnected">Disconnect</button>'
    }
}

const startDisconnect = function() {
    client.disconnect();
    buttonChange(true);
}
const onConnectionLost = function(responseObject) {
    if (responseObject.errorCode !== 0) { // write error message to html 
        console.log(responseObject.errorMessage);
    }
    buttonChange(true);
}
const onFail = function() {
    console.log(`Connection to: ${host} on port: ${port} failed.`)
    buttonChange(true);
}

const onConnect = function() {
    topic = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";

    console.log(`Subscribing to: ${topic}`)

    client.subscribe(topic);

    cars.forEach(car=>{
        car.orderCar(0);
    });

    buttonChange(false);
}

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

const onMessageArrived = function(message){
    if (message.payloadString.slice(-2) === ']]'){
        console.log(message)
        jsonObject = getJsonData(message.payloadString);

        cars.forEach(car => {
            if (jsonObject[0] === car.name){
                car.messagesCarHTML(message.payloadString, true);
                car.carAct(jsonObject[1]);
            }
        });
    }
}

const startConnect = function() {
    const host = "maqiatto.com";
    const port = 8883;
    const username = "simon.ogaardjozic@abbindustrigymnasium.se";
    const password = "scavenger";

    console.log("lamao")

    client = new Paho.MQTT.Client(host, Number(port), clientID);
    
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    client.connect({
        userName : username, 
        password : password,
        onSuccess: onConnect,
        onFailure: onFail,
    });
}