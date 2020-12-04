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
bufferStart = 40
read_data = None
read_data_decode = None

ALL_ROI = [0, 0, CameraWidth, CameraHeight]
bothV = 90
bothX = sensor.width()/2
matrix = [0, 0, 0, 0]

focusPoint = [CameraWidth/2, CameraHeight/5]

### Variabler ###
GREENE_THRESHOLDS = [(0, 100, -20, -128, -128, 127)]
GRAY_THRESHOLDS = [(180, 255)]

ALPHA_DARKEN = 57
THETA_TILT = 10
PEDESTRIAN_CROSSING_PIXELS = 2500

LEFT_LANE_ROI = [0, 0, int(CameraWidth/3), CameraHeight]
RIGHT_LANE_ROI = [int(CameraWidth/1.5), 0, CameraWidth, CameraHeight]
MIDDLE_LANE_ROI = [0, int(CameraHeight/1.5), CameraWidth, CameraHeight]

### Uart ###
fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)
uart_A = UART(UART.UART1, 115200, 8, None, 0, timeout=1000, read_buf_len=4096)

fm.register (board_info.PIN10, fm.fpioa.UART2_RX)
uart_B = UART (UART.UART2, 115200, 8, None, 1, timeout = 1000, read_buf_len = 4096)

### Yolo2 ###
classes = ["lego gubbe"]
task = kpu.load(0x600000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)

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

        self.sensor.set_gainceiling(8)
        self.sensor.set_vflip(False)
        self.sensor.set_hmirror(False)
        self.sensor.set_auto_exposure(True)

        self.sensor.set_windowing((width, height))

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

    if yoloObj:
        for object in yoloObj:
            img_.draw_rectangle(object.rect(), (0, 255, 0), 2, False)
            img_.draw_string(object.x(), object.y(), str(object.value()), color=(255,0,0), scale=1.5)

        return 1, img_
    return 0, img_

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

def getClosestToFocusPoint(object_):
    if object_:
        l = [math.sqrt((obj.cx()-focusPoint[0])**2 + (obj.cy()-focusPoint[1])**2) for obj in object_]
        object = object_[l.index(min(l))]
        return (object.cx(), object.cy())
    return (0,0)

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
    # print(JSON)

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
    buffer = bufferStart
    camera = cameraSetup(224, 224)

    while buffer > 0:
        img = camera.takeImg()
        legoGubbar, img = getYoloObjects(img)
        camera.displayImg(img)

        if legoGubbar:
            buffer = bufferStart
        buffer-=1

    buffer = bufferStart
    camera = cameraSetup(CameraWidth, CameraHeight)

    while True:
        img = camera.takeImg()

        obstacle = getColoredObjects(img, GREENE_THRESHOLDS, 500, 4, 2, 5, ALL_ROI)
        closestObject = getClosestToFocusPoint(obstacle)

        laneAppropiate = laneAppropriateImg(img, [obstacle])
        leftLaneLine = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, LEFT_LANE_ROI)
        rightLaneLine = getLaneLine(laneAppropiate, GRAY_THRESHOLDS, 20, True, 4, 2, RIGHT_LANE_ROI)

        leftCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, LEFT_LANE_ROI, 50)
        rightCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, RIGHT_LANE_ROI, 50)
        middleCrossing = getPedestrianCrossing(laneAppropiate, GRAY_THRESHOLDS, 4, 2, MIDDLE_LANE_ROI, 50)

        bothV, bothX, new = getSteerValues([leftLaneLine, rightLaneLine], bothV, bothX)
        matrix = getRoadType(img, [0,0,0,0], bothV, leftCrossing, rightCrossing, middleCrossing)

        outlineObjects(img, obstacle, (0, 255, 0), 2, False)
        markPoint(img, closestObject, 3, (255, 255, 0), 1, True)
        drawLine(img, [leftLaneLine, rightLaneLine], (0, 0, 0), 2)
        drawMap(img, [[0,matrix[0],0],[matrix[3],1,matrix[1]],[0,matrix[2],0]], 5)

        if buffer > 0:
            if closestObject[0] and closestObject[1]:
                buffer = bufferStart
            buffer-=1
            transferValues(matrix, closestObject)
        else:
            transferValues(matrix, int(bothV), int(bothX))

            try:
                read_data = uart_B.read()
                if read_data is not None:
                    read_data_decode = read_data.decode('utf-8')
                    if read_data_decode == "[Observe]":
                        break
            except:
                pass

        camera.displayImg(img)
