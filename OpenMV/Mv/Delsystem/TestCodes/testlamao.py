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

### Biblotek ###
import sensor, lcd, math, json
from fpioa_manager import fm
from machine import UART
from board import board_info
import KPU as kpu

### Sensor ###
lcd.init()


### Yolo2 ###
classes = ["Legogubbe"]
task = kpu.load(0x600000)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828)
kpu.init_yolo2(task, 0.70, 0.3, 5, anchor)

class carSetup:
    def __init__(self, width, height):

        ### Init ###

        self.width = width
        self.height = height

        self.color = (0, 255, 0)
        self.border = 2
        self.fill = False

        self.sensor = sensor

        self.sensor.reset()
        self.sensor.set_pixformat(sensor.RGB565)
        self.sensor.set_framesize(sensor.QVGA)

        self.sensor.set_contrast(-2)
        self.sensor.set_gainceiling(16)
        self.sensor.set_vflip(False)
        self.sensor.set_hmirror(False)

        self.sensor.set_windowing((self.width,self.height))

        self.sensor.run(1)

        ### Variable ###

        self.ALL_ROI = [0, 0, self.sensor.width(), self.sensor.height()]
        self.bothV = 90
        self.bothX = self.sensor.width()/2
        self.matrix = [0, 0, 0, 0]

        self.RED_THRESHOLDS = [(0, 100, 127, 20, 127, -128)]
        self.GREENE_THRESHOLDS = [(0, 100, -20, -128, -128, 127)]
        self.BLUE_THRESHOLDS = [(0, 100, -128, 127, -128, -15)]
        self.ROAD_JOINTS_THRESHOLDS = [(0, 100, 127, 20, 127, -128)]
        self.GRAY_THRESHOLDS = [(200, 255)]

        self.ALPHA_DARKEN = 57
        self.THETA_TILT = 10
        self.PEDESTRIAN_CROSSING_PIXELS = 2500

        self.LEFT_LANE_ROI = [0, 0, int(self.width/3), self.height]
        self.RIGHT_LANE_ROI = [int(self.width/1.5), 0, self.width, self.height]
        self.MIDDLE_LANE_ROI = [0, int(self.height/1.5), self.width, self.height]

        ### Uart ###
        fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)
        self.uart_A = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000, read_buf_len=4096)

    ### Funktioner ###

    def camera(self):
        self.img = sensor.snapshot()
        return self.img

    def displaypic(self):
        lcd.display(self.img)

    ### Beräkningar ###

    def getYoloObject(self):
        self.yoloObj = kpu.run_yolo2(task, self.img)
        if self.yoloObj:
            for object in self.yoloObj:
                self.img.draw_rectangle(object.rect(), self.color, self.border, self.fill)
        return 1 if self.yoloObj else 0

    def getColoredObjects(self, img_, threshold_, pixelthreshold_, xstride_, ystride_, margin_, roi_):
        return img_.find_blobs(threshold_, x_stride = xstride_, y_stride = ystride_, pixels_threshold = pixelthreshold_, merge = True, margin = margin_, roi = roi_)

    def laneAppropriateImg(self, img_, roi_):
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

    def getPedestrianCrossing(self, img_, threshold_, xstride_, ystride_, roi_, margin_):
        pedestrianCrossings = getColoredObjects(img_, threshold_, 0, xstride_, ystride_, margin_, roi_)
        crossingArea = sum([obj.pixels() for obj in pedestrianCrossings])
        return True if crossingArea >= PEDESTRIAN_CROSSING_PIXELS else False

    def getLaneLine(self, img_, threshold_, pixelthreshold_, robust_, xstride_, ystride_, roi_):
        laneLine = img_.get_regression((threshold_), pixels_threshold = pixelthreshold_, robust = robust_, x_stride = xstride_, y_stride = ystride_, roi = roi_)
        return laneLine

    def getClosestToCenter(self, object_):
        if object_:
            l = [math.sqrt((obj.cx()-sensor.width()/2)**2 + (obj.cy()-sensor.height()/2)**2) for obj in object_]
            object = object_[l.index(min(l))]
            return (object.cx(), object.cy())
        return 0

    def getSteerValues(self, lines_, bothV_, bothX_):
        new = False
        if lines_[0] and lines_[1]:
            new = True
            leftV = lines_[0].theta()+90 if lines_[0].theta() < 90 else abs(lines_[0].theta()-90)
            rightV = lines_[1].theta()+90 if lines_[1].theta() < 90 else abs(lines_[1].theta()-90)
            bothV_ = (leftV+rightV) / 2
            bothX_ = (lines_[0].x2() + lines_[1].x2())/2 - sensor.width()/2
        return bothV_, bothX_, new

    def getRoadType(self, img_, matrix_, bothV_, leftCrossing_, rightCrossing_, middleCrossing_):
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

    def transferValues(self, *values_):
        JSON = json.dumps(values_)
        uart_A.write(JSON)
        print(JSON)

    ### Visuellt ###
    def outlineObjects(self, img_, objects_, color_, border_, fill_):
        for object in objects_:
            img_.draw_rectangle(object.rect(), color_, border_, fill_)

    def markPoint(self, img_, xy_, radius_, color_, thickness_, fill_):
        if xy_:
            img_.draw_circle(xy_[0], xy_[1], radius_, color_, thickness_, fill_)

    def drawLine(self, img_, line_, color_, thickness_):
        for lines in line_:
            if lines:
                img_.draw_line(lines.line(), color_, thickness_)

    def drawMap(self, img_, matrix_, scale_):
        x, y = 0, 0
        for amount1, row in enumerate(matrix_):
            for amount2, col in enumerate(row):
                img_.draw_rectangle([x,y,scale_,scale_], (0,0,0) if col==0 else (255,255,255) if col==1 else (255,0,0), 1, True)
                x += scale_
            x = 0
            y += scale_

while True:
    
    car = carSetup(320,240)

    while True:
        img = car.camera()

        # Objekt
        uraniumRods = car.getColoredObjects(img, car.GREENE_THRESHOLDS, 500, 4, 2, 5, car.ALL_ROI)
        redRods = car.getColoredObjects(img, car.RED_THRESHOLDS, 500, 4, 2, 5, car.ALL_ROI)
        blueRods = car.getColoredObjects(img, car.BLUE_THRESHOLDS, 500, 4, 2, 5, car.ALL_ROI)

        allObjects = uraniumRods + redRods + blueRods
        closestObject = getClosestToCenter(allObjects)
        closestObject = 0


        # Väg
        laneAppropiate = car.laneAppropriateImg(img, [allObjects])
        leftLaneLine = car.getLaneLine(laneAppropiate, car.GRAY_THRESHOLDS, 20, True, 4, 2, car.LEFT_LANE_ROI)
        rightLaneLine = car.getLaneLine(laneAppropiate, car.GRAY_THRESHOLDS, 20, True, 4, 2, car.RIGHT_LANE_ROI)

        leftCrossing = car.getPedestrianCrossing(laneAppropiate, car.GRAY_THRESHOLDS, 4, 2, car.LEFT_LANE_ROI, 50)
        rightCrossing = car.getPedestrianCrossing(laneAppropiate, car.GRAY_THRESHOLDS, 4, 2, car.RIGHT_LANE_ROI, 50)
        middleCrossing = car.getPedestrianCrossing(laneAppropiate, car.GRAY_THRESHOLDS, 4, 2, car.MIDDLE_LANE_ROI, 50)

        bothV, bothX, new = car.getSteerValues([leftLaneLine, rightLaneLine], bothV, bothX)

        ## Skicka över alla värden ##
        matrix = car.getRoadType(img, [0,0,0,0], bothV, leftCrossing, rightCrossing, middleCrossing)
        # matrix = [1,1,1,1]
        car.transferValues(closestObject, matrix, bothV, bothX)

        # Visuellt
        car.outlineObjects(img, uraniumRods, (0, 255, 0), 2, False)
        car.outlineObjects(img, redRods, (255, 0, 0), 2, False)
        car.outlineObjects(img, blueRods, (0, 0, 255), 2, False)

        car.markPoint(img, closestObject, 3, (255, 255, 0), 1, True)
        car.drawLine(img, [leftLaneLine, rightLaneLine], (0, 0, 0), 2)
        car.drawMap(img, [[0,matrix[0],0],[matrix[3],1,matrix[1]],[0,matrix[2],0]], 5)


        # if CheckForLegoGubbar:
        #     break

    # car = carSetup(224,224)
    # legoGubbar = True
    # for _ in range(25):
    #     while legoGubbar:
    #         img = car.camera()
    #         legoGubbar = car.yolo()
    #         lcd.display(img)
    #     else:
    #         img = car.takepic()
    #         lcd.display(img)
