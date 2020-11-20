const dev = false;

// Universal constants
const mapDimensions = [6, 6];
const maxMapDimensions = Math.max(...mapDimensions);
const mapDimensionsExtended = maxMapDimensions*2-1;
const clientID = "clientID_" + parseInt(Math.random() * 100);

const orderArray = [0,1,null,2];

const arrayCorespondingImage = {
    straight: [1, 0, 1, 0],
    curve_left: [0, 0, 1, 1],
    curve_right: [0, 1, 1, 0],
    three_way_left: [1, 0, 1, 1],
    three_way_right: [1, 1, 1, 0],
    three_way: [0, 1, 1, 1],
    four_way: [1, 1, 1, 1]
};

let variables = window.localStorage.getItem('variable');
const buttonForVariables = document.getElementById("variables");
buttonForVariables.innerHTML = `<input type="text" id="variable" name="variable" value="${variables}"><button onclick="sendCarVariable('variable')">sendVariable</button>`

// Universal calculation functions
let mapSkeleton1 = [];
let mapSkeleton2 = [];
for(let y=0; y<mapDimensionsExtended; y++) {
    mapSkeleton1[y] = [];
    mapSkeleton2[y] = [];
    for(let x=0; x<mapDimensionsExtended; x++) {
        mapSkeleton1[y][x] = null;
        mapSkeleton2[y][x] = null;
    }
}

const rotationReset = function(rotation){
    if (rotation < 0) {
        return rotation + 360;
    } else if (rotation >= 360){
        return rotation - 360;
    }
    return rotation;
}

const arrayRotate = function(array, rotation){
    let arrayCopy = [...array];
    for (let i = 0; i < Math.abs(rotation/90); i++) {
        arrayCopy.unshift(arrayCopy.pop());
    }
    return arrayCopy;
}

const arraysMatch = function(arr1, arr2) {
	if (arr1.length !== arr2.length){ 
        return false;
    }
	for (let i = 0; i < arr1.length; i++) {
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

const validCoord = function(coord){
    if (coord[0]<0 || coord[0]>mapDimensionsExtended-1 || coord[1]<0 || coord[1]>mapDimensionsExtended-1){
        return false;
    }
    return true;
}

// Cars Functions
// functions that calculate stuff
const carDrive = function(car, roadArray){
    const mapPovArray = arrayRotate(roadArray, car.rotation);
    car.map[car.viewCoord[0]][car.viewCoord[1]] = [...mapPovArray];

    // TODO
    const order = getMultipleCarOrders(car);

    statusUpdateHTML(car, `Driving ${order}`)

    if(dev){
        messagesCarHTML(car, `[${car.name}, ${order}]`,false)
        car.recentOrder = order;
    } else {
        setTimeout(orderCar(car, order), 1000);
    }

    // in the future (when car has moved)
    if (car.recentOrder === 1 || arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
        car.rotation+=90;
    } else if (car.recentOrder === 2 || arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
        car.rotation-=90;
    }
    car.rotation = rotationReset(car.rotation);

    car.carCoord = [car.viewCoord[0],car.viewCoord[1]];
    car.viewCoord[0] = car.viewCoord[0]+Math.round(Math.sin(car.rotation*Math.PI/180));
    car.viewCoord[1] = car.viewCoord[1]+Math.round(Math.cos(car.rotation*Math.PI/180));

    moveCarHTML(car, roadArray);
}

const getMultipleCarOrders = function(car){
    let treeBranch = [car.rotation, [...car.viewCoord],[]];
    let tree = [];
    let foundMissing = false;
    let i = 0;
    
    tree.push(treeBranch);

    console.log("waaa" + tree)

    while (!foundMissing){

        tree[i][2] = getOrdersForBranch(tree[i][0], tree[i][1], car.map);

        console.log("Tree");
        console.log(tree[i][2]);
        console.log(tree[i][2].length)
        for (let n=0; n<tree[i][2].length; n++){
            console.log(tree[i][2][n][1]);
            if (tree[i][2][n][1]){
                return tree[i][2][n][0];
            }
        }

        let treeBranch = [];
        tree.push(treeBranch);

        console.log("WHAAAAAAAAAAAAAA");
        console.log(tree);

        // nu ska du itterera igenom 

        return 0;
        i++;
    }
}

const getOrdersForBranch = function(rotation, coord, map){ // ANVÄND validCoord TODO !!!!!!!!!!!!
    console.log("rotation " + rotation)
    let availableOrder = [];
    let roadArrayCopy = [];

    const roadArray = [...map[coord[0]][coord[1]]];
    for (let i=0; i<4; i++){
        roadArrayCopy[i] = [roadArray[i], orderArray[i], null, null];
    }

    // rotera denna
    const surroundningMap = [
        [coord[0], coord[1]+1],
        [coord[0]+1, coord[1]],
        [coord[0], coord[1]-1],
        [coord[0]-1, coord[1]]
    ];
    // const rightRotationSurroundingMap = arrayRotate(surroundningMap, rotationReset(-rotation));
    const carPOVRoadArray = arrayRotate(roadArrayCopy, rotation);
    let coordXY=null;
    // let rotatedCoordXY=null;

    console.log("carcoord "+coord)

    for (let xy=0; xy<4; xy++){
        // rotatedCoordXY = rightRotationSurroundingMap[xy];
        coordXY = surroundningMap[xy];
        // console.log("lookingForCoordXY "+coordXY+" RotatedCoordXY "+rotatedCoordXY)
        // console.log(rotatedCoordXY)
        console.log(validCoord(coordXY))
        if (validCoord(coordXY)){
            carPOVRoadArray[xy][2] = map[coordXY[0]][coordXY[1]];
            if (carPOVRoadArray[xy][2]){
                carPOVRoadArray[xy][3] = [coordXY[0],coordXY[1]];
            }    
        } else{
            carPOVRoadArray[xy][1]=null;
        }
    }

    // upp är inte upp upp är vänster
    // kolla validcoord vid denna for loop
    console.log("carPOVRoadArray")
    console.log(carPOVRoadArray)

    // const carPOVRoadArray = arrayRotate(roadArrayCopy, rotationReset(-rotation));
    let newRotation=null;

    for (let i=0; i<4; i++){
        newRotation = rotation;

        if (carPOVRoadArray[i][1] === 1 || arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
            console.log("AAAAAAA")
            if (arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
                carPOVRoadArray[i][1] = 1;
            }
            newRotation+=90;
        } else if (carPOVRoadArray[i][1] === 2 || arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
            console.log("AAAAAAA")
            if (arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
                carPOVRoadArray[i][1] = 1;
            }
            newRotation-=90;
        }
        newRotation = rotationReset(newRotation);
        console.log("look below")
        console.log(carPOVRoadArray[i][0], carPOVRoadArray[i][1])
        console.log(roadArrayCopy[i][0], roadArrayCopy[i][1])
        if (roadArrayCopy[i][0] && carPOVRoadArray[i][1] !== null){ // roadArrayCopy[i][1] or carPOVRoadArray[i][1] ????
            availableOrder.push([carPOVRoadArray[i][1], !carPOVRoadArray[i][2], carPOVRoadArray[i][3], newRotation]);
        }
    };
    
    console.log(availableOrder.sort(function(a,b){return a[0]-b[0];}))
    // availableOrder.sort(function(a,b){return a[1].localeCompare(b[1]);});
    // sortera availableOrder beroende på deras availableOrder[i][0]

    return availableOrder.sort(function(a,b){return a[0]-b[0];});
}

const orderCar = function(car, order){
    let orderMessage = new Paho.MQTT.Message(`["${car.name}", "${order}"]`);
    orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    client.send(orderMessage);
    messagesCarHTML(car, `["${car.name}", "${order}"]`, false);
    car.recentOrder = order;
}

// functions that change car html
const carInOrigoHTML = function(car){
    const carOrigoContainer = document.getElementById(`X${car.name}:${car.carCoord[0]},${car.carCoord[1]}`);
    carOrigoContainer.classList.add(`imgCar`);
    carOrigoContainer.classList.add(`rotate(${car.rotation}deg)`);
    
    const carLookingOrigoContainer = document.getElementById(`X${car.name}:${car.viewCoord[0]},${car.viewCoord[1]}`);
    carLookingOrigoContainer.classList.add(`imgLook`);
}
const moveCarHTML = function(car, roadArray){
    imageDir = returnImageDirOfArray(roadArray);
    const imageElement = document.getElementById(`${car.name}:${car.carCoord[0]},${car.carCoord[1]}`);
    imageElement.src = imageDir;

    const oldCarDiv = document.querySelector(`.car${car.name} .imgCar`);
    oldCarDiv.classList.remove("imgCar");
    imageElement.style.transform = oldCarDiv.style.transform;

    const newCarDiv = document.querySelector(`.car${car.name} .imgLook`);
    newCarDiv.classList.remove("imgLook");
    newCarDiv.classList.add(`imgCar`);
    newCarDiv.style.transform = `rotate(${car.rotation}deg)`;

    const carNewLook = document.getElementById(`X${car.name}:${car.viewCoord[0]},${car.viewCoord[1]}`);
    carNewLook.classList.add(`imgLook`);
    carNewLook.style.transform = `rotate(${car.rotation}deg)`;
}
const statusUpdateHTML = function(car, message) {
    const containerForStatus = document.querySelector(`.car${car.name}Status`);
    containerForStatus.innerHTML = `Car is: ${message}`;
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

// Cars
let cars = [
    Simon = {
        isConnected: 0,
        name: "S",

        carCoord: [maxMapDimensions-1, maxMapDimensions-1],
        viewCoord: [maxMapDimensions-1, maxMapDimensions],
        rotation: 0,

        map: mapSkeleton1,

        recentOrder: 0,
    },
    Khe = {
        isConnected: 0,
        name: "K",

        carCoord: [maxMapDimensions-1, maxMapDimensions-1],
        viewCoord: [maxMapDimensions-1, maxMapDimensions],
        rotation: 0,

        map: mapSkeleton2,

        recentOrder: 0,
    }
]

// Html Init
const createMap = function(mapDimensions, id){
    const containerForMap = document.querySelector(`.carMap${id}`);

    for (let y = mapDimensions[1]-1; y >= 0; y--) {
        containerForMap.innerHTML += `<div class="axisY" id="Y${id}:${y}"></div>`;
        
        for (let x = 0; x < mapDimensions[0]; x++) {
            const containerY = document.getElementById(`Y${id}:${y}`);
            containerY.innerHTML += `<span class="axisX roadImage"><img class="roadImage" id="${id}:${x},${y}" src="Images/PNG/missing.png" style="transform: rotate(0deg);"><div id="X${id}:${x},${y}"></div></span>`;
        }
    }
}

createMap(mapDimensions,"Both");

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

    let orderMessage = new Paho.MQTT.Message(`u good bro?`);
    orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";

    client.subscribe(topic)
    client.send(orderMessage)
    buttonChange(false);
}

const sendCarVariable = function(variable){
    window.localStorage.setItem("variable", document.getElementById(variable).value);
    variables = window.localStorage.getItem('variable');

    let orderMessage = new Paho.MQTT.Message(`["S",${variables}]`);
    orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    client.send(orderMessage);
    console.log(variables)
}

const sendCarOrder = function(carName){
    let value = document.getElementById(carName).value;
    cars.forEach(car=>{
        if (car.name === value || value === "A"){
            orderCar(car, 3)
        }
    })
}

const getJsonData = function(JSON_DATA){
    const road_probability = 0.65
    const JSON_array = JSON.parse(JSON_DATA);
    const JSON_road_type = JSON_array[1];
    let road_array = [];
    
    for(let i = 0; i < JSON_road_type.length; i++) {
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
        let jsonObject = getJsonData(message.payloadString);
        if (jsonObject[1].length === 4){
            cars.forEach(car => {
                if (jsonObject[0] === car.name){
                    messagesCarHTML(car, message.payloadString, true);
                    carDrive(car, jsonObject[1]);
                }
            });
        }
    } else if (message.payloadString.slice(-11) === 'HasDriven"]') {
        let jsonObject = getJsonData(message.payloadString);
        cars.forEach(car => {
            if (jsonObject[0] === car.name){
                statusUpdateHTML(car, `Observing`)
                messagesCarHTML(car, message.payloadString, true);
                orderCar(car, 3);
            }
        });
    } else if (message.payloadString.slice(-11) === 'Connected"]'){
        let jsonObject = getJsonData(message.payloadString);
        cars.forEach(car => {
            if (jsonObject[0] === car.name){
                if(car.isConnected){
                    console.log("wait did car loose connect? myues it did")
                } else {
                    car.isConnected = 1;
                    createMap([mapDimensionsExtended,mapDimensionsExtended], car.name);
                    carInOrigoHTML(car);
                    messagesCarHTML(car, message.payloadString, true);
                }
            }
        });
    }
}

const devOnMessageArrived = function(message){
    console.log(message);
    if (message.slice(-2) === ']]'){
        let jsonObject = getJsonData(message);

        cars.forEach(car => {
            if (jsonObject[0] === car.name){
                messagesCarHTML(car, message, true);
                carDrive(car, jsonObject[1]);
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


const devSendJSON = function(id){
    let value = document.getElementById(id).value;
    let message = `["${id}",${value}]`;
    console.log(value, message)
    devOnMessageArrived(message);
}