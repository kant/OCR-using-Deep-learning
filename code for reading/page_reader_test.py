from pprint import pprint as pp
import keras
import numpy as np
import copy
import cv2


img_size = 32

charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

model = keras.models.load_model('model/keras_new.model')


def show_contours(image, contours):
    cp = copy.copy(image)
    cv2.drawContours(cp, contours, -1, (0, 0, 255), 1)
    cv2.imshow('contours', cp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def preprocess_image(image):
    gray_blur = cv2.GaussianBlur(image, (15, 15), 0)
    thresh = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)
    return thresh


def pad_scale_sample(image):
    scale_factor = img_size / image.shape[0]
    new_x = round(image.shape[1] * scale_factor)
    image = cv2.resize(image, dsize=(new_x, img_size), fx=scale_factor, fy=scale_factor)
    border = cv2.copyMakeBorder(image, top=0, bottom=0, left=16, right=16, borderType=cv2.BORDER_CONSTANT, value=255)
    return border


def single_inferance(img):
    #img = np.expand_dims(img, axis=2)
    #img = np.expand_dims(img, axis=0)
    cv2.imshow('just before recognising',img)

    cv2.waitKey(200)
    cv2.destroyAllWindows()
    preds, = model.predict(img)
    print('chup')
    print(preds)

    lst = list(preds)
    result = []
    for i in range(len(lst)):
        crtnty = float(lst[i])
        if crtnty < 0.5:
            continue
        ltr = charset[i]
        if ltr == 'Q':
            continue
        result.append((ltr, crtnty))
    return result



def scan_image(image):
    results = []
    idx = 0
    while True:

        print('heyo')
        sample = image[0:img_size, idx:idx+img_size+30]
        idx += 8
        cv2.imshow('scaled and padded sample', sample)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        inferance = single_inferance(sample)
        results.append(inferance)
        pp(inferance)

        print('ohohoh')

        return results


if __name__ == "__main__":
    img = cv2.imread('real_tests/pan.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    thresh = preprocess_image(img)
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
    print('num contours found', len(contours))
    #show_contours(thresh, contours)
    for contour in contours:

        area = cv2.contourArea(contour)
        if area > 40:
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            img1 = cv2.drawContours(img, [box], -1, (255, 255, 255), 0)
            x, y, w, h, = cv2.boundingRect(contour)
            # if sample is too small, probably just artifact
            ratio = w / h
            if ratio > 5:
                continue
            sample = img[y:y+h, x:x+w]  # take a sample out of the original image
            #cv2.imshow('hey', img)
            #cv2.waitKey(100)
            sample = pad_scale_sample(sample)  # scale to 32px high and pad sides for scanning
            predictions = scan_image(sample)
            print(predictions)


cv2.imshow('hey',img)
cv2.waitKey(100)
cv2.imshow('hey2',sample)
cv2.waitKey(100)
cv2.imshow('hey1',thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()