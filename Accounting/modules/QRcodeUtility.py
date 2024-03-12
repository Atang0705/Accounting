import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import ImageFont, ImageDraw, Image


def putText(x,y,text,color=(0,0,0)):
    # global img
    fontpath = 'NotoSansTC-Light.ttf'
    font = ImageFont.truetype(fontpath, 20)
    imgPil = Image.fromarray(img)
    draw = ImageDraw.Draw(imgPil)
    draw.text((x, y), text, fill=color, font=font)
    img = np.array(imgPil)

def boxSize(arr):
    global data
    box_roll = np.rollaxis(arr,1,0)
    xmax = int(np.amax(box_roll[0]))
    xmin = int(np.amin(box_roll[0]))
    ymax = int(np.amax(box_roll[1]))
    ymin = int(np.amin(box_roll[1]))
    return (xmin,ymin,xmax,ymax)

def QRcodeRead(img_path):
    img = cv2.imread(img_path)

    barcodes = decode(img)

    print(barcodes[0].data.decode("utf-8"))
    qrcodetext = ['','']
    for barcode in barcodes:
        # 检查条码类型是否为二维条码
        if barcode.type == 'QRCODE':
            barcodeData = barcode.data.decode("utf-8")
            if barcodeData.startswith('**'):
                qrcodetext[1] = barcodeData
            else:
                qrcodetext[0] = barcodeData

    return qrcodetext


    