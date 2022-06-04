import cv2
import pytesseract
import numpy as np
import glob
from pdf2image import convert_from_path
import os
import re
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract"


def tempMatch(img, templ, method=cv2.TM_CCOEFF_NORMED):
    # TM_CCOEFF_NORMED
    _, w, h = templ.shape[::-1]
    templHeightAndWidth = (w, h)

    img = cv2.GaussianBlur(img, (7, 7), 0, 0)
    templ = cv2.GaussianBlur(templ, (7, 7), 0, 0)
    res = cv2.matchTemplate(templ, img, method)
    if method == cv2.TM_SQDIFF_NORMED:
        weight = 1 - np.amin(res)
        (max_val, min_val, max_loc, min_loc) = cv2.minMaxLoc(res)
    else:
        weight = np.amax(res)
        (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(res)

    # weight = np.amax(res)
    # (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(res)
    templCornerPoints = list((min_val, max_val, min_loc, max_loc))

    return templCornerPoints, weight



def get_ocr(img):

    _,thre = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    kernel = np.ones((3,1), np.uint8)

    # U May need to use one of these two
    img_erosion = cv2.erode(thre, kernel, iterations=1)
    img_dilation = cv2.dilate(thre, kernel, iterations=1)

    # cv2.imshow('Erosion', img_erosion)
    # cv2.imshow('Dilation', img_dilation)

    s = pytesseract.image_to_string(img_dilation,lang='Eng')
    print(s)
    return s



def get_titile(file):
    template = cv2.imread("./Template.png")
    w, h = template.shape[:-1]
    # Store Pdf with convert_from_path function
    images = convert_from_path(file)
    query = np.array(images[0])
    corner, weight = tempMatch(query, template)
    bottom_right = (int(corner[3][0] + h), int(corner[3][1] + w))
    left = (int(corner[3][0]), int(corner[3][1]))
    color = [255, 0, 0]
    #     query = cv2.rectangle(query,left,bottom_right,color , 2)
    query_gray = cv2.cvtColor(query, cv2.COLOR_BGR2GRAY)
    thr = cv2.threshold(query_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    kerenal = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 3))
    morph_img = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kerenal)
    contors, _ = cv2.findContours(morph_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    padding = 20
    titile_s = "Not Found"
    for c in contors:
        xs, ys, ws, hs = cv2.boundingRect(c)
        if abs(ys - corner[3][1]) < 30 and cv2.contourArea(c) > 1000:
            #             cv2.drawContours(query,[c],-1,(0,255,0),3)
            cv2.rectangle(query, (xs, ys), (xs + ws, ys + hs), color, 2)
            titile_img = thr[ys - padding:ys + hs + padding, xs - padding:xs + ws + padding]
            titile_s = get_ocr(titile_img)
            titile_s = titile_s.replace("\n", "")
            titile_s = titile_s.replace("/", "")
            titile_s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', titile_s)
            titile_s = titile_s.replace("\n0c", "")

            if ":" in titile_s:
                titile_s = titile_s.split(":")[1]


    return titile_s,query