import cv2
import numpy as np
import os

def read_images(category):
    images = category + '/input/in%06d.jpg'
    cap = cv2.VideoCapture(images)
    return cap

def frame_diff(category):
    cap = read_images(category)
    res_path_frm = 'results/' + category + '/frame_diff/'
    _, first_frame = cap.read(0)
    first_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    first_gray = cv2.GaussianBlur(first_gray, (5, 5), 0)
    i=1 #counter for the output images
    cap = read_images(category) #To start from the beginning
    while True:
        _, frame = cap.read()
        if np.shape(frame) == ():
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        difference = cv2.absdiff(first_gray, gray_frame)
        _, difference = cv2.threshold(difference, 50, 255, cv2.THRESH_BINARY)

        cv2.imshow("First frame", first_frame)
        cv2.imshow("Frame", frame)
        cv2.imshow("difference", difference)

        #Outputs to the result folder
        cv2.imwrite(os.path.join(res_path_frm,'out%06d.jpg' %i), difference)
        i+=1

        key = cv2.waitKey(10)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    eval(category,i,res_path_frm)

def median_filter(category):
    cap = read_images(category)
    res_path_med = 'results/' + category + '/median_filter/'
    #history=100, varThreshold=50
    subtractor = cv2.createBackgroundSubtractorMOG2(history=50, varThreshold=50, detectShadows=True)
    i=1
    while True:
        _, frame = cap.read()
        if np.shape(frame) == ():
            break
        mask = subtractor.apply(frame)
        cv2.imshow("Frame", frame)
        cv2.imshow("mask", mask)

        #Outputs to the result folder
        cv2.imwrite(os.path.join(res_path_med,'out%06d.jpg' %i), mask)
        i+=1

        key = cv2.waitKey(10)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    eval(category,i,res_path_med)

#highway 470, office 570, pedestrian 300
def eval(category,last,res_path):
    acc = []
    gt_path = category + '/groundtruth/'
    #start from first ground truth available
    if category == 'highway':
        i = 470
    elif category == 'office':
        i = 570
    else:
        i = 300

    while i < last:
        #pr: prediction vs gt: ground truth
        pr_1 = cv2.imread(os.path.join(res_path,'out%06d.jpg' %i))
        gt_1 = cv2.imread(os.path.join(gt_path,'gt%06d.png' %i))
        c = (np.sum(abs(pr_1 -  gt_1)) / np.sum(gt_1))

        acc.append(1-c)
        i+=1

    #remove nans and infs from the accuracy list
    acc = [x for x in acc if ~np.isnan(x) and ~np.isinf(x)]
    print('Accuracy:', np.mean(acc))

categories = ['highway','office','pedestrians']

for cat in categories:
    print('showing frame differencing for ' + cat)
    frame_diff(cat)
    print('showing median filtering for ' + cat)
    median_filter(cat)
