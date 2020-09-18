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
};

// Universal calculation functions
let mapSkeletonS = [];
let mapSkeletonK = [];
for(let y=0; y<mapDimensionsExtended[1]; y++) {
    mapSkeletonS[y] = [];
    mapSkeletonK[y] = [];
    for(var x=0; x<mapDimensionsExtended[0]; x++) {
        mapSkeletonS[y][x] = [null, null];
        mapSkeletonK[y][x] = [null, null];
    }
}

const arrayRotate = function(roadArray, rotation) {
    let roadArrayCopy = [...roadArray];
    let anotherArrayLOL = [0,1,null,2];
    for (let i = 0; i < Math.abs(rotation/90); i++) {
        if (rotation > 0){
            roadArrayCopy.unshift(roadArrayCopy.pop());
            anotherArrayLOL.unshift(anotherArrayLOL.pop());
        } else{
            roadArrayCopy.push(roadArrayCopy.shift());
            anotherArrayLOL.push(anotherArrayLOL.shift());
        } 
    }
    const rotatedRoadArray = {
        N: [roadArrayCopy[0],roadArray[0],anotherArrayLOL[0]], 
        E: [roadArrayCopy[1],roadArray[1],anotherArrayLOL[1]],
        S: [roadArrayCopy[2],roadArray[2],anotherArrayLOL[2]],
        W: [roadArrayCopy[3],roadArray[3],anotherArrayLOL[3]]
    };
    return rotatedRoadArray;
}

const arraysMatch = function(arr1, arr2) {
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
            return `Images/PNG/${key}.png`;
        }
    }
}


// Cars Functions
// functions that calculate stuff
const carHasCleanedRoadAheadAndIsReadyToDrive = function(car, roadArray){
    updateMapHTML(car, roadArray);

    const rotatedRoadArray = arrayRotate(roadArray, car.rotation); 
    const order = getCarOrder(car, roadArray, rotatedRoadArray);
    orderCar(car, order);

    car.map[car.viewCoord[0]][car.viewCoord[1]][0] = [...roadArray];
    car.map[car.viewCoord[0]][car.viewCoord[1]][1] = rotatedRoadArray;

    // in the future (when car has moved)
    if (car.recentOrder === 1 || arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
        car.rotation+=90;
    } else if (car.recentOrder === 2 || arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
        car.rotation-=90;
    }

    car.carCoord = [car.viewCoord[0],car.viewCoord[1]];
    car.viewCoord[0] = car.viewCoord[0]+Math.round(Math.sin(car.rotation*Math.PI/180));
    car.viewCoord[1] = car.viewCoord[1]+Math.round(Math.cos(car.rotation*Math.PI/180));

    carIsDriving(car);
}

const carIsDriving = function(car){
    const oldCarDiv = document.querySelector(`.car${car.name} .imgCar`);
    oldCarDiv.classList.remove("imgCar");

    const lastClass = oldCarDiv.classList.item(oldCarDiv.classList.length-1);
    oldCarDiv.classList.remove(lastClass);
    oldCarDiv.style.transform = lastClass;

    const newCarDiv = document.querySelector(`.car${car.name} .imgLook`);
    newCarDiv.classList.remove("imgLook");
    newCarDiv.classList.add(`imgCar`);
    newCarDiv.classList.add(newCarDiv.style.transform);
    newCarDiv.style.transform = `rotate(${car.rotation}deg)`;

    const carNewLook = document.getElementById(`${car.name}:${car.viewCoord[0]},${car.viewCoord[1]}`);
    carNewLook.classList.add(`imgLook`);
    carNewLook.style.transform = `rotate(${car.rotation}deg)`;
}
const getCarOrder = function(car, roadArray, rotatedRoadArray){
    if (roadArray.reduce((a, b) => a + b, 0) == 2){
        return 0;
    }

    const surroundingFromMapPOV = {
        N: car.map[car.viewCoord[0]][car.viewCoord[1]+1][0],
        E: car.map[car.viewCoord[0]+1][car.viewCoord[1]][0],
        S: car.map[car.viewCoord[0]][car.viewCoord[1]-1][0],
        W: car.map[car.viewCoord[0]-1][car.viewCoord[1]][0]
    };

    let carOrdersAvailable = [];
    for (const key in surroundingFromMapPOV){
        console.log(surroundingFromMapPOV[key], rotatedRoadArray[key], key)
        if (!surroundingFromMapPOV[key] && rotatedRoadArray[key][1] && rotatedRoadArray[key][2] !== null){
            // right now it goes N>E>W from car pov
            carOrdersAvailable.push(rotatedRoadArray[key][2]);
        }
    };
    return carOrdersAvailable.sort(function(a, b) {return a - b})[0];
}
const orderCar = function(car, order){
    console.log(`[${car.name}, ${order}]`);
    let orderMessage = new Paho.MQTT.Message(`[${car.name}, ${order}]`);
    orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    client.send(orderMessage);
    messagesCarHTML(car, `[${car.name}, ${order}]`,false)
    car.recentOrder = order;
}

// functions that change car html
const carInOrigoHTML = function(car){
    const carOrigoContainer = document.getElementById(`${car.name}:${car.carCoord[0]},${car.carCoord[1]}`);
    carOrigoContainer.classList.add(`imgCar`);
    carOrigoContainer.classList.add(`rotate(${car.rotation}deg)`);
    
    const carLookingOrigoContainer = document.getElementById(`${car.name}:${car.viewCoord[0]},${car.viewCoord[1]}`);
    carLookingOrigoContainer.classList.add(`imgLook`);
}
const messagesCarHTML = function(car, message, msgFromCar){
    let className = null;
    if (msgFromCar){
        className = `.car${car.name}Sent`;
    } else {
        className = `.car${car.name}Received`;
    }
    const containerForMessages = document.querySelector(className);
    containerForMessages.innerHTML += `${message}<br>`;
}
const updateMapHTML = function(car, roadArray){
    imageDir = returnImageDirOfArray(roadArray);
    const imageElement = document.querySelector(`.carMap${car.name} .imgLook`);
    imageElement.src = imageDir;
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
    },
    Khe = {
        name: "K",

        carCoord: [mapDimensions[0]-1, mapDimensions[1]-1],
        viewCoord: [mapDimensions[0]-1, mapDimensions[1]],
        rotation: 0,

        map: mapSkeletonK,

        recentOrder: 0,
    }
]

// Html Init
const createMap = function(mapDimensions, id){
    const containerForMap = document.querySelector(`.carMap${id}`);

    for (let y = mapDimensions[1]-1; y >= 0; y--) {
        containerForMap.innerHTML += `<div class="axisY" id="${id}:${y}"></div>`;
        
        for (let x = 0; x < mapDimensions[0]; x++) {
            const containerY = document.getElementById(`${id}:${y}`);
            containerY.innerHTML += `<img class="roadImage" id="${id}:${x},${y}" src="Images/PNG/missing.png" style="transform: rotate(0deg);">`;
        }
    }
}

createMap(mapDimensions,"Both");
cars.forEach(car=>{
    createMap(mapDimensionsExtended, car.name);
    carInOrigoHTML(car);
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
        orderCar(car, 0); // 3 igentligen just fyi
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
    console.log(message.payloadString);
    if (message.payloadString.slice(-2) === ']]'){
        jsonObject = getJsonData(message.payloadString);

        cars.forEach(car => {
            if (jsonObject[0] === car.name){
                messagesCarHTML(car, message.payloadString, true);
                carHasCleanedRoadAheadAndIsReadyToDrive(car, jsonObject[1]);
            }
        });
    }
}

const startConnect = function() {
    const host = "maqiatto.com";
    const port = 8883;
    const username = "simon.ogaardjozic@abbindustrigymnasium.se";
    const password = "scavenger";

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

// change html div and css class to look right 

// make a better plan'd route (send 1,2 or 3 depending on best choise)
// mby a* algorythm

// after the order is sent:
// we will place an transparant image of the car over the newly changed car coord that is correctly rotated

// add status message for each car, aka im cleaning, or im driving etc