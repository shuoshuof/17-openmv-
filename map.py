import sensor, image, time,tf
from machine import UART
import time
import pyb
from pyb import LED
from machine import Pin
import openmv_numpy as np

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA) # we run out of memory if the resolution is much bigger...像素为160*120
sensor.set_brightness(2000) # 设置图像亮度 越大越亮
sensor.skip_frames(time = 100)
sensor.set_auto_gain(True)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(True)  # must turn this off to prevent image washout...
sensor.set_auto_exposure(False,100)



world_coordinates = [[40,140],
                   [180,140],
                   [180,40],
                   [40,40]]

#返回透视矩阵
def cal_mtx(XY:np.array,UV:np.array)->np.array:
    A = []
    B =[]
    for i in range(4):
        a = [[XY[i][0],XY[i][1],1,0,0,0,-UV[i][0]*XY[i][0],-UV[i][0]*XY[i][1]],
             [0,0,0,XY[i][0],XY[i][1],1,-UV[i][1]*XY[i][0],-UV[i][1]*XY[i][1]]]
        B+= [[UV[i][0]],
             [UV[i][1]]]
        A+=a

    A = np.array(A)
    B = np.array(B)

    x= np.solve(A,B)

    H = [[x[0][0], x[1][0], x[2][0]],
         [x[3][0], x[4][0], x[5][0]],
         [x[6][0], x[7][0], 1]]

    return np.array(H)

def map(img):
    
    for r in img.find_rects(threshold = 10000):
        #img.draw_rectangle(r.rect(), color = (255, 0, 0))
        point_num=0
        if r.w()>=200 and r.h()>=100 and r.w()<=300 and r.h()<=300:
            img.draw_rectangle(r.rect(), color = (255, 0, 0))
            print(r.rect())
            img_coordinate=[]

            points =[]
            for c in img.find_circles(roi =r.rect(),threshold = 1500, x_margin = 10, y_margin = 10, r_margin = 10,r_min = 2, r_max =6, r_step = 1):


                c_roi=(c.x()-c.r(),c.y()-c.r(),2*c.r(),2*c.r())
                threshold = (0, 58, -87, 127,-128, 127)
                blobs = img.find_blobs([threshold],roi = c_roi, pixels_threshold=int(0.2*4*c.r()*c.r()), area_threshold=1,
                                        merge=True, margin=10, invert=False)
                img.draw_circle(c.x(), c.y(),2, color = (0, 255, 0),thickness = 4)
                if len(blobs):
                    points.append([c[0], c[1], 1])

            if show:
                for p in r.corners():
                    img.draw_circle(p[0], p[1], 2, color = (0, 0, 255))
                    img_coordinate.append([p[0], p[1]])

            img_coordinate[0][1]-=3
            img_coordinate[1][1]-=3
            point_num += 1
            return  img_coordinate,points
    return None,None


show =True
if __name__ == '__main__':
    while(True):
        img = sensor.snapshot()
        #img = img.lens_corr(strength = 0.8, zoom = 1.0).histeq(adaptive=True, clip_limit=3)

        img_coordinate,points =map(img)#地图识别

        if img_coordinate==None:
            continue

        img_coordinate =np.array(img_coordinate)
        world_coordinates =np.array(world_coordinates)

        H= cal_mtx(img_coordinate,world_coordinates)


        real_point = []
        img.draw_rectangle(40,40,140,100, color = (0, 0, 255))

        show_points=[]
        for c in points:

            coord = np.array([[p] for p in c])#升维
            point = H*coord#透视变换

            x,y = point[0][0]/point[2][0],point[1][0]/point[2][0]
            #点不会太靠近边界
            if x>=40+5 and x<180-5 and y>=40+5 and y<=140-5:
                if show:
                    img.draw_circle(c[0], c[1], 3, color=(255, 0, 0), thickness=4)

                img.draw_circle(int(x), int(y),2, color = (0, 0, 255),thickness = 4)
                x,y = x-40,100-y+(40)
                x,y = (x*5),(y*5)
                show_points.append([x//20+1,y//20+1])
                x = (x//20)*20+10
                y = (y//20)*20+10
                real_point.append([int(x),int(y)])
                        