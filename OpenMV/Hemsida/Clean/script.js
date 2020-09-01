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
    // console.log(arr1, arr2)
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
            // console.log(arrayCorespondingImage[key], key)
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
        carHasCleanedRoadAheadAndIsReadyToDrive: function(roadArray){
            this.updateMapHTML(roadArray);

            const rotatedRoadArray = arrayRotate(roadArray, this.rotation);
            const order = this.getCarOrder(roadArray);
            this.orderCar(order);

            this.map[this.viewCoord[0]][this.viewCoord[1]][0] = [...roadArray];
            this.map[this.viewCoord[0]][this.viewCoord[1]][1] = [...rotatedRoadArray];

            // in the future (when car has moved)
            if (this.recentOrder === 1 || arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
                this.rotation+=90;
            } else if (this.recentOrder === 2 || arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
                this.rotation-=90;
            }

            this.carCoord = [this.viewCoord[0],this.viewCoord[1]];
            this.viewCoord[0] = this.viewCoord[0]+Math.round(Math.sin(this.rotation*Math.PI/180));
            this.viewCoord[1] = this.viewCoord[1]+Math.round(Math.cos(this.rotation*Math.PI/180));

            this.carIsDriving();
        },
        carIsDriving: function(){
            const oldCarDiv = document.querySelector(`.car${this.name} .imgCar`);
            oldCarDiv.classList.remove("imgCar");

            // console.log(oldCarDiv.classList, typeof(oldCarDiv.classList),oldCarDiv.classList.length);
            const lastClass = oldCarDiv.classList.item(oldCarDiv.classList.length-1);
            // console.log(lastClass)
            oldCarDiv.classList.remove(lastClass);
            oldCarDiv.style.transform = lastClass;

            // oldCarDiv.classList.remove(-1);
            // console.log("AAAAAAAAAAAAAAAA");
            // console.log(oldCarDiv);
            // console.log(oldCarDiv.id[1]);
            // oldCarDiv.style.transform = oldCarDiv.id[1];
            // console.log(oldCarDiv);
            // where car goes away, reset rotation
            // oldCarDiv.id.remove("")






            // const newCarDiv = document.getElementById(`${this.name}:${this.carCoord[0]},${this.carCoord[1]}`);
            const newCarDiv = document.querySelector(`.car${this.name} .imgLook`);
            // console.log(`${this.name}:${this.carCoord[0]},${this.carCoord[1]}`);
            // console.log(newCarDiv)
            newCarDiv.classList.remove("imgLook");
            newCarDiv.classList.add(`imgCar`);

            // REMOVE ROTATE CLASS FROM LOOK DIV
            // const lastClassLook = newCarDiv.classList.item(newCarDiv.classList.length-1);
            // newCarDiv.classList.remove(lastClassLook);
            // newCarDiv.style.transform = lastClassLook;


            newCarDiv.classList.add(newCarDiv.style.transform);
            newCarDiv.style.transform = `rotate(${this.rotation}deg)`;
            // remove car class and its rotation from this div
            // add car class with its individual rotation

            const carNewLook = document.getElementById(`${this.name}:${this.viewCoord[0]},${this.viewCoord[1]}`);
            carNewLook.classList.add(`imgLook`);
            // carNewLook.classList.add(carNewLook.style.transform);
            carNewLook.style.transform = `rotate(${this.rotation}deg)`;
        },
        
        getCarOrder: function(roadArray){
            if (roadArray.reduce((a, b) => a + b, 0) == 2){
                // console.log("XD")
                return 0;
            }
        },
        orderCar: function(order){
            let orderMessage = new Paho.MQTT.Message(`[${this.name}, ${order}]`);
            orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
            client.send(orderMessage);
            this.recentOrder = order;
        },
        
        // functions that change html
        carInOrigoHTML: function(){
            const carOrigoContainer = document.getElementById(`${this.name}:${this.carCoord[0]},${this.carCoord[1]}`);
            carOrigoContainer.classList.add(`imgCar`);
            carOrigoContainer.classList.add(`rotate(${this.rotation}deg)`);
            
            const carLookingOrigoContainer = document.getElementById(`${this.name}:${this.viewCoord[0]},${this.viewCoord[1]}`);
            carLookingOrigoContainer.classList.add(`imgLook`);
            // carLookingOrigoContainer.classList.add(`rotate(${this.rotation}deg)`);
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
            // const imageElement = document.getElementById(`${this.name}:${this.viewCoord[0]},${this.viewCoord[1]}`);
            const imageElement = document.querySelector(".carMapS .imgLook");
            // console.log(imageElement);
            // console.log(`${this.name}:${this.viewCoord[0]},${this.viewCoord[1]}`);
            // imageElement.style.transform = `rotate(${this.rotation}deg)`; // IS THIS NECESARY???
            imageElement.src = imageDir;

            // if (this.recentOrder != 3)
            
            // uuuh, somewhere else?
            // const carElement = document.querySelector(".carMapS .imgCar");
            // carElement.classList.remove("imgCar");

            // console.log(carElement.classList[1]);
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
            containerY.innerHTML += `<img class="roadImage" id="${id}:${x},${y}" src="Images/PNG/missing.png" style="transform: rotate(0deg);">`;
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
        car.orderCar(3);
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
        jsonObject = getJsonData(message.payloadString);

        cars.forEach(car => {
            if (jsonObject[0] === car.name){
                car.messagesCarHTML(message.payloadString, true);
                car.carHasCleanedRoadAheadAndIsReadyToDrive(jsonObject[1]);
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

// (init) send order 3 to all cars ✔

// they are now picking things upp @ this.viewcoord ✔
// when they are done they will send the map back ✔
// gotten map will contain car name and road array ✔

// we want to update html correctly (rotated road on right coord) ✔
// and use this gained info to plan next route (meh, "plan")
// this will create our new objective (navigate on top of view'd road)
// too achive this we will be sending 1,2 or 3 depending on best choise


// after the order is sent:
// we will place an transparant image of the car over the newly changed car coord that is correctly rotated


// when they have navigated they will send done, now reset this "loop"


// add status message for each car, aka im cleaning, or im driving etc