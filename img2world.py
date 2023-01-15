import sensor, image, time
from machine import UART
import time
import pyb
from pyb import LED
from machine import Pin
import openmv_numpy as np
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)#160,120 320,240
sensor.skip_frames(time = 2000)
sensor.set_auto_exposure(True)


#A4纸参数
#可以换成其它
a4_w = 297
a4_h = 210

world_coordinates = [[(-a4_w/2),0],[a4_w/2,0],[(a4_w/2),a4_h],[(-a4_w/2),a4_h]]

#返回透视矩阵
#XY为世界坐标，UV为相机坐标
def cal_mtx(UV:np.array,XY:np.array)->np.array:
    A = []
    B =[]
    for i in range(4):
        a = [[UV[i][0],UV[i][1],1,0,0,0,-XY[i][0]*UV[i][0],-XY[i][0]*UV[i][1]],
             [0,0,0,UV[i][0],UV[i][1],1,-XY[i][1]*UV[i][0],-XY[i][1]*UV[i][1]]]
        B+= [[XY[i][0]],
             [XY[i][1]]]
        A+=a

    A = np.array(A)
    B = np.array(B)

    x= np.solve(A,B)

    H = [[x[0][0], x[1][0], x[2][0]],
         [x[3][0], x[4][0], x[5][0]],
         [x[6][0], x[7][0], 1]]

    return np.array(H)

show =True
while(True):
    img = sensor.snapshot()

    for r in img.find_rects(threshold = 20000):
        img.draw_rectangle(r.rect(), color = (255, 0, 0))
        img_coordinate=[]
        print("********")
        if show:
            for p in r.corners():
                img.draw_circle(p[0], p[1], 2, color = (0, 255, 0))
                img_coordinate.append([p[0]-80, 120-p[1]])
                print(p[0]-80,120-p[1])
        dn_cx = (img_coordinate[0][0]+img_coordinate[1][0])/2
        dn_cy = (img_coordinate[1][0]+img_coordinate[1][1])/2
        up_cx = (img_coordinate[2][0]+img_coordinate[3][0])/2
        up_cy = (img_coordinate[2][1]+img_coordinate[3][1])/2
        print((dn_cx+up_cx)/2)
        #居中判定
        if abs((dn_cx-up_cx)/(dn_cy-up_cy))<=0.05 and abs((dn_cx+up_cx)/2)<=5:
            img_coordinate =np.array(img_coordinate)
            world_coordinates =np.array(world_coordinates)

            H= cal_mtx(img_coordinate,world_coordinates)
            #pyb.mdelay(1000)
            print(H)
        print()
    img.draw_line(80, 120, 80, 0, color = (255, 0, 0), thickness = 1)
