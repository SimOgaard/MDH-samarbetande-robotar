const dev = true;

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

// Universal calculation functions
let mapSkeleton1 = [];
let mapSkeleton2 = [];
for(let y=0; y<mapDimensionsExtended; y++) {
    mapSkeleton1[y] = [];
    mapSkeleton2[y] = [];
    for(var x=0; x<mapDimensionsExtended; x++) {
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

const validCoord = function(coord){
    if (coord[0]<0 || coord[1]<0 || coord[0]>maxMapDimensions-1 || coord[1]>maxMapDimensions-1){
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

    if(dev){
        messagesCarHTML(car, `[${car.name}, ${order}]`,false)
        car.recentOrder = order;
    } else {
        orderCar(car, order);
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


//                                         //  null means cant go, 0 means can go but known road is there, 1 means can go and unknown road is there
// [90,[5,5],[null, 1, 0]] = [rotation, coord, [orde1, order2, order3]]


// [
//                                                 [0,1,2], 
// //                                          <-     v      ->
//                                      [[0,1,2],  [0,1,2],  [0,1,2]]
// //                              <-                 v                  ->
//    [[[0,1,2],  [0,1,2],  [0,1,2]],   [[0,1,2],  [0,1,2],  [0,1,2]],   [[0,1,2],  [0,1,2],  [0,1,2]]]
// ]


const getMultipleCarOrders = function(car){
    let treeBranch = [car.rotation, [...car.viewCoord],[]];
    let tree = [];
    let foundMissing = false;
    let i = 0;
    
    tree.push(treeBranch);

    console.log("waaa" + tree)

    while (!foundMissing){

        tree[i][2] = getOrdersForBranch(tree[i][0], tree[i][1], car.map);

        console.log(tree)

        for (n=0; n<tree[i][2].length; n++){
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

const getOrdersForBranch = function(rotation, coord, map){ // rotationen är fel?

    let availableOrder = [];
    let roadArrayCopy = [];

    const roadArray = [...map[coord[0]][coord[1]]];
    for (i=0; i<4; i++){
        roadArrayCopy[i] = [roadArray[i], orderArray[i], null, null];
    }

    roadArrayCopy[0][2] = map[coord[0]][coord[1]+1];
    roadArrayCopy[1][2] = map[coord[0]+1][coord[1]];
    roadArrayCopy[2][2] = map[coord[0]][coord[1]-1];
    roadArrayCopy[3][2] = map[coord[0]-1][coord[1]];

    if (roadArrayCopy[0][2]){
        roadArrayCopy[0][3] = [coord[0],coord[1]+1];
    }
    if (roadArrayCopy[1][2]){
        roadArrayCopy[1][3] = [coord[0]+1,coord[1]];
    }
    if (roadArrayCopy[2][2]){
        roadArrayCopy[2][3] = [coord[0],coord[1]-1];
    }
    if (roadArrayCopy[3][2]){
        roadArrayCopy[3][3] = [coord[0]-1,coord[1]];
    }

    const carPOVRoadArray = arrayRotate(roadArrayCopy, rotationReset(-rotation));

    let newRotation;
    for (i=0; i<4; i++){
        newRotation = rotation;

        if (roadArrayCopy[i][1] === 1 || arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
            if (arraysMatch(roadArray, arrayCorespondingImage.curve_right)){
                roadArrayCopy[i][1] = 1;
            }
            newRotation+=90;
        } else if (roadArrayCopy[i][1] === 2 || arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
            if (arraysMatch(roadArray, arrayCorespondingImage.curve_left)){
                roadArrayCopy[i][1] = 1;
            }
            newRotation-=90;
        }
        newRotation = rotationReset(newRotation);

        if (carPOVRoadArray[i][0] && roadArrayCopy[i][1] !== null){
            availableOrder.push([roadArrayCopy[i][1], !carPOVRoadArray[i][2], carPOVRoadArray[i][3], newRotation]);
        }
    };
    
    console.log(availableOrder)
    return availableOrder;
}


// [[1,2,1,0,0,0,1],[0,1,2]]





// const getAvailableCarOrdersOutcome = function(car, rotatedRoadArray, viewCoord){
//     const surroundingFromMapPOV = {
//         N: car.map[viewCoord[0]][viewCoord[1]+1][0],
//         E: car.map[viewCoord[0]+1][viewCoord[1]][0],
//         S: car.map[viewCoord[0]][viewCoord[1]-1][0],
//         W: car.map[viewCoord[0]-1][viewCoord[1]][0]
//     };

//     let carOrdersAvailable = [];
//     for (const key in surroundingFromMapPOV){
//         if (roadArray && rotatedRoadArray[key][1] !== null){
//             carOrdersAvailable.push([rotatedRoadArray[key][1], !surroundingFromMapPOV[key]]);
//         }
//     };

//     return carOrdersAvailable;
// }

// // ge funktionen cordinater och den ska ge tilbacka vilka actions den kan ta och vad som finns där
// const getAvailableCarOrdersOutcome = function(priorActions, carMap, viewCoord, rotation){
//     let roadArrayKey = ["N","E","S","W"];
//     let rotatedRoadArrayKey = rotateSingleArray(roadArrayKey, rotation) // roterad verition av rotatedRoadArray beroende på din rotation
//     let rotatedRoadArray = carMap[viewCoord[0]][viewCoord[1]][1];
//     let availableCarOrders = [];

//     const surroundingFromMapPOV = {
//         N: carMap[viewCoord[0]][viewCoord[1]+1][0],
//         E: carMap[viewCoord[0]+1][viewCoord[1]][0],
//         S: carMap[viewCoord[0]][viewCoord[1]-1][0],
//         W: carMap[viewCoord[0]-1][viewCoord[1]][0]
//     };

//     let order = null;
//     let missing = null;
//     let key = null;
//     for (keyIndex=0; keyIndex<4; keyIndex++){
//         keyCar = rotatedRoadArrayKey[keyIndex];
//         keyMap = roadArrayKey[keyIndex];

//         if (roadArray[keyCar] && rotatedRoadArray[keyMap][1] !== null){
//             order = rotatedRoadArray[keyMap][1];
//             // if (!surroundingFromMapPOV[key]){
//             //     missing = true
//             // } else {
//             //     missing = false
//             // }
//             missing = !surroundingFromMapPOV[key];
//             availableCarOrders.push([order, missing]);
//         }
//     }
//     // for (const key in surroundingFromMapPOV){
//     //     if (roadArray[key] && rotatedRoadArray[key][1] !== null){
//     //         order = rotatedRoadArray[key][1];
//     //         // if (!surroundingFromMapPOV[key]){
//     //         //     missing = true
//     //         // } else {
//     //         //     missing = false
//     //         // }
//     //         missing = !surroundingFromMapPOV[key];
//     //         availableCarOrders.push([order, missing]);
//     //     }
//     // };

// }
//     // om jag står såhär här:
//         // (prior actions) vilka coords jag ser och vilken rotation jag har; behöver functionen
//         // exempel: [[0,1,0,1,1,2], [3,2], 420]

//         // nu med detta:
//             // vad befinner sig där jag kollar? car.map[x][y]
//             // vart kan jag åka?
//             // vad är där?
        
//     // return (prior actions), [available actions, if action lead to missing]
//     // example: [[0,1,0,1,1,2], [[0, false],[1, true],[2, false]]]


// // nu när du har [[0,1,0,1,1,2], [[0, false],[1, true],[2, false]]]:
// // kolla om några är true:
//     // om de är true return (prior actions).push(available action that leads to missing); [0,1,0,1,1,2].push(action[0])
// // annars:
//     // getAvailableCarOrdersOutcome([0,1,0,1,1,2].push(action[0])

// const getOptimalCarOrder = function(car, orders){
//     // meh gå bara igenom alla
//     // sedan kolla vilken som leder till minst orders.length
//     // och skicka tillbaka den
// }
// const getMultipleCarOrder = function(car, roadArray){
//     let orders = [];
//     let viewCoord = car.viewCoord;
//     let rotation = car.rotation;
//     let roadArrayAtCoord = roadArray;

//     while (true){
//         const rotatedRoadArray = arrayRotate(roadArray, car.rotation)
//         const availableCarOrders = getAvailableCarOrdersOutcome(car, rotatedRoadArray, viewCoord);
        
//         for (let i=0; i<availableCarOrders.length; i++){
//             if (availableCarOrders[i][1] === null){
//                 orders.push(availableCarOrders[i][0])
//                 return orders
//             }    
//         }

//         choosenOrder = getOptimalCarOrder(availableCarOrders, roadArrayAtCoord);

//         // choose order
//         // ändra rotation och coord
//         orders.push(choosenOrder);

//         if (choosenOrder === 1 || arraysMatch(roadArrayAtCoord, arrayCorespondingImage.curve_right)){
//             rotation+=90;
//         } else if (choosenOrder === 2 || arraysMatch(roadArrayAtCoord, arrayCorespondingImage.curve_left)){
//             rotation-=90;
//         }

//         viewCoord[0] = viewCoord[0]+Math.round(Math.sin(rotation*Math.PI/180));
//         viewCoord[1] = viewCoord[1]+Math.round(Math.cos(rotation*Math.PI/180));

//         roadArrayAtCoord = car.map[viewCoord[0]][viewCoord[1]][0];
//     }
// }

// const getMultipleCarOrders = function(car, roadArray){

// }






const orderCar = function(car, order){
    console.log(`[${car.name}, ${order}]`);
    let orderMessage = new Paho.MQTT.Message(`[${car.name}, ${order}]`);
    orderMessage.destinationName = "simon.ogaardjozic@abbindustrigymnasium.se/Scavenger";
    client.send(orderMessage);
    messagesCarHTML(car, `[${car.name}, ${order}]`, false)
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
        name: "S",

        carCoord: [maxMapDimensions-1, maxMapDimensions-1],
        viewCoord: [maxMapDimensions-1, maxMapDimensions],
        rotation: 0,

        map: mapSkeleton1,

        recentOrder: 0,
    },
    Khe = {
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
cars.forEach(car=>{
    createMap([mapDimensionsExtended,mapDimensionsExtended], car.name);
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
                carDrive(car, jsonObject[1]);
            }
        });
    } else if (message.payloadString.slice(-6) === 'ready]'){
        let data = JSON.parse(message.payloadString)
        cars.forEach(car => {
            if (data[0] === car.name){
                messagesCarHTML(car, message.payloadString, true);
            }
        });
    }
}

const devOnMessageArrived = function(message){
    console.log(message);
    if (message.slice(-2) === ']]'){
        jsonObject = getJsonData(message);

        cars.forEach(car => {
            if (jsonObject[0] === car.name){
                messagesCarHTML(car, message, true);
                carDrive(car, jsonObject[1]);
            }
        });
    } else if (message.slice(-6) === 'ready]'){
        let data = JSON.parse(message)
        cars.forEach(car => {
            if (data[0] === car.name){
                messagesCarHTML(car, message, true);
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