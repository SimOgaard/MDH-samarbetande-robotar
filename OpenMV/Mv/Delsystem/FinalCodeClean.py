### TODO:
    # laneAppropiateImage               Copy binary version of image, invertera (not), använd som mask för mörkning. Tanken är att bara det ljusa ska bli mörkare. Fler itterationer? så att det ljusaste blir mörare än det lite ljusa
    #                                   Testa även multipy add subtract divide images, kolla om de gör som ovan om inte bättre
    # Snabbare funktioner               Tex image.clear() "verry fast" till skillnad från drawsquare. Även hur du använder numpy "vertecees" kunde adderas ihop tusen ggr snabbare än for loopar
    # Värden på:
    #           tresholds,
    #           osv
    # Yolo                              Få den att funka med copy och lite ram
    # uh
    # img_.copy(roi=YOLO_ROI, copy_to_fb=False).to_rgb565(copy=False) kanske har kvar hela bilden men pekar mot roi

### TODO WITH LEGO BUILD, balk mellan L så det blir en triangel

### Biblotek ###
import sensor, lcd, math, json
from fpioa_manager import fm
from machine import UART
from board import board_info
import KPU as kpu

### Konstanter ###
CameraWidth = 320
CameraHeight = 240
drivenOneRoad = False

ALL_ROI = [0, 0, CameraWidth, CameraHeight]
bothV = 90
bothX = sensor.width()/2
matrix = [0, 0, 0, 0]

### Variabler ###
RED_THRESHOLDS = [(0, 100, 127, 20, 127, -128)]
GREENE_THRESHOLDS = [(0, 100, -20, -128, -128, 127)]
BLUE_THRESHOLDS = [(0, 100, -128, 127, -128, -15)]
ROAD_JOINTS_THRESHOLDS = [(0, 100, 127, 20, 127, -128)]
GRAY_THRESHOLDS = [(200, 255)]

ALPHA_DARKEN = 57
THETA_TILT = 10
PEDESTRIAN_CROSSING_PIXELS = 2500

LEFT_LANE_ROI = [0, 0, int(CameraWidth/3), CameraHeight]
RIGHT_LANE_ROI = [int(CameraWidth/1.5), 0, CameraWidth, CameraHeight]
MIDDLE_LANE_ROI = [0, int(CameraHeight/1.5), CameraWidth, CameraHeight]

### Uart ###
fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)
uart_A = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000, read_buf_len=4096)

### Yolo2 ###
classes = ["lego gubbe"]
task = kpu.load(0x600000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
kpu.init_yolo2(task, 0.7, 0.3, 5, anchor)

### Funktioner ###

### Sensor ###
class cameraSetup:
    def __init__(self, width, height):
        self.lcd = lcd
        self.sensor = sensor

        self.lcd.init()
        self.sensor.reset()
        self.sensor.set_pixformat(sensor.RGB565)
        self.sensor.set_framesize(sensor.QVGA)

        self.sensor.set_gainceiling(16)
        self.sensor.set_vflip(False)
        self.sensor.set_hmirror(False)
        self.sensor.set_auto_exposure(True)

        self.sensor.set_windowing((width,height))

        self.sensor.run(1)

    def takeImg(self):
        return self.sensor.snapshot()

    def displayImg(self, img):
        self.lcd.display(img)

### Beräkningar ###
def getColoredObjects(img_, threshold_, pixelthreshold_, xstride_, ystride_, margin_, roi_):
    return img_.find_blobs(threshold_, x_stride = xstride_, y_stride = ystride_, pixels_threshold = pixelthreshold_, merge = True, margin = margin_, roi = roi_)

def getYoloObjects(img_):
    yoloObj = kpu.run_yolo2(task, img_)
    return 1 if yoloObj else 0

def laneAppropriateImg(img_, roi_):
    img_copy = img_.to_grayscale(copy = True, rgb_channel = (0/1/2))

    lights = getColoredObjects(img_copy, GRAY_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
    if lights:
        l = [obj.pixels() for obj in lights]
        light = lights[l.index(max(l))]
        img_copy_roi = img_copy.copy(roi=light.rect(), copy_to_fb=False).clear()
        img_copy = img_copy.draw_image(img_copy_roi, light.x(), light.y(), alpha=ALPHA_DARKEN)

    for roi in roi_:
        outlineObjects(img_copy, roi, (0, 0, 0), 1, True)
    return img_copy

def getPedestrianCrossing(img_, threshold_, xstride_, ystride_, roi_, margin_):
    pedestrianCrossings = getColoredObjects(img_, threshold_, 0, xstride_, ystride_, margin_, roi_)
    crossingArea = sum([obj.pixels() for obj in pedestrianCrossings])
    return True if crossingArea >= PEDESTRIAN_CROSSING_PIXELS else False

def getLaneLine(img_, threshold_, pixelthreshold_, robust_, xstride_, ystride_, roi_):
    laneLine = img_.get_regression((threshold_), pixels_threshold = pixelthreshold_, robust = robust_, x_stride = xstride_, y_stride = ystride_, roi = roi_)
    return laneLine

def getClosestToCenter(object_):
    if object_:
        l = [math.sqrt((obj.cx()-sensor.width()/2)**2 + (obj.cy()-sensor.height()/2)**2) for obj in object_]
        object = object_[l.index(min(l))]
        return (object.cx(), object.cy())
    return 0

def getSteerValues(lines_, bothV_, bothX_):
    new = False
    if lines_[0] and lines_[1]:
        new = True
        leftV = lines_[0].theta()+90 if lines_[0].theta() < 90 else abs(lines_[0].theta()-90)
        rightV = lines_[1].theta()+90 if lines_[1].theta() < 90 else abs(lines_[1].theta()-90)
        bothV_ = (leftV+rightV) / 2
        bothX_ = (lines_[0].x2() + lines_[1].x2())/2 - sensor.width()/2
    return bothV_, bothX_, new

def getRoadType(img_, matrix_, bothV_, leftCrossing_, rightCrossing_, middleCrossing_):
    matrix_[2] = 1
    if not leftCrossing_ and not rightCrossing_ and middleCrossing_:
        matrix_[3] = 1
        matrix_[1] = 1
    else:
        if leftCrossing_ or bothV_ <= 90-THETA_TILT:
            matrix_[3] = 1
        if rightCrossing_ or bothV_ >= 90+THETA_TILT:
            matrix_[1] = 1
        if bothV_ > 90-THETA_TILT and bothV_ < 90+THETA_TILT:
            matrix_[0] = 1
    return matrix_

def transferValues(*values_):
    JSON = json.dumps(values_)
    uart_A.write(JSON)
    print(JSON)

### Visuellt ###
def outlineObjects(img_, objects_, color_, border_, fill_):
    for object in objects_:
        img_.draw_rectangle(object.rect(), color_, border_, fill_)

def markPoint(img_, xy_, radius_, color_, thickness_, fill_):
    if xy_:
        img_.draw_circle(xy_[0], xy_[1], radius_, color_, thickness_, fill_)

def drawLine(img_, line_, color_, thickness_):
    for lines in line_:
        if lines:
            img_.draw_line(lines.line(), color_, thickness_)

def drawMap(img_, matrix_, scale_):
    x, y = 0, 0
    for amount1, row in enumerate(matrix_):
        for amount2, col in enumerate(row):
            img_.draw_rectangle([x,y,scale_,scale_], (0,0,0) if col==0 else (255,255,255) if col==1 else (255,0,0), 1, True)
            x += scale_
        x = 0
        y += scale_

while True:

    camera = cameraSetup(CameraWidth, CameraHeight)

    while True:
        img = camera.takeImg()

        # Objekt
        uraniumRods = getColoredObjects(img, GREENE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
        redRods = getColoredObjects(img, RED_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
        blueRods = getColoredObjects(img, BLUE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)

        allObjects = uraniumRods + redRods + blueRods
        # closestObject = getClosestToCenter(allObjects)
        closestObject = 0

        # Yolo
        # legoGubbar = getYoloObjects(img)
        # legoGubbar = 0

        # Väg
        laneAppropiate = laneAppropriateImg(img, [allObjects])
        leftLaneLine = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, LEFT_LANE_ROI)
        rightLaneLine = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, RIGHT_LANE_ROI)

        leftCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, LEFT_LANE_ROI, 50)
        rightCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, RIGHT_LANE_ROI, 50)
        middleCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, MIDDLE_LANE_ROI, 50)

        bothV, bothX, new = getSteerValues([leftLaneLine, rightLaneLine], bothV, bothX)

        ## Skicka över alla värden ##
        matrix = getRoadType(img, [0,0,0,0], bothV, leftCrossing, rightCrossing, middleCrossing)
        # matrix = [1,1,1,1]
        transferValues(closestObject, matrix, bothV, bothX)

        # Visuellt
        outlineObjects(img, uraniumRods, (0, 255, 0), 2, False)
        outlineObjects(img, redRods, (255, 0, 0), 2, False)
        outlineObjects(img, blueRods, (0, 0, 255), 2, False)

        markPoint(img, closestObject, 3, (255, 255, 0), 1, True)
        drawLine(img, [leftLaneLine, rightLaneLine], (0, 0, 0), 2)
        drawMap(img, [[0,matrix[0],0],[matrix[3],1,matrix[1]],[0,matrix[2],0]], 5)

        camera.displayImg(laneAppropiate)

        if drivenOneRoad:
            break

    legoGubbar = True
    camera = cameraSetup(224, 224)

    for _ in range(25):
        while legoGubbar:
            img = camera.takeImg()
            legoGubbar = getYoloObjects(img)
            camera.displayImg(img)
        else:
            img = camera.takeImg()
            lcd.displayImg(img)
