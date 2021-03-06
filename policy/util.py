# -*- coding: utf-8 -*-

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
import numpy as np
import csv
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from pandas import DataFrame
import pandas as pd
import os, sys
import json

#defining needed functions
"""
Suffle multiple arrays with respect of its indexing
Args:
    arrs: list of arrays of same length
Returns:
    list of shuffled arrays
"""
def shuffle_arrs (arrs):
    p = np.random.permutation (len(arrs[0]))
    return [arr[p] for arr in arrs]

"""
Removes specified @proportion of records which satisfies condition from given arrays (@arrs)
with respect of its indexing. Removing is based on specified array (@arr_idx) values.
Values of array are testing with @condition_lambda and dividing into two parts.
First part that satisfies @condition_lambda and second which is not.
Next first part is suffled and sparsed by @proportion, concatenated with second and returned.
Other array values will be sparsed correspondingly

You can use this function to remove portion of records with some specific values from
dataset represented by list of arrays

Args:
    proportion: floating point value from 0 to 1
    condition_lambda: lambda which will be used fot testing values of specified array
    arr_idx: index in array list which points to array that will be used for selecting values
    arrs: list of arrays

Returns:
    list of arrays
"""
def sparse_arrays_by_first_array_value (proportion, condition_lambda, arr_idx, arrs):
    
    target_arr = arrs [arr_idx]
    idx_less = np.where(condition_lambda(target_arr))
    idx_greater = np.where(np.logical_not(condition_lambda(target_arr)))

    less_arrs = [arr[idx_less] for arr in arrs]
    greater_arrs = [arr[idx_greater] for arr in arrs]

    less_arrs = shuffle_arrs (less_arrs)

    proportion_count = int(proportion * len (less_arrs[arr_idx]))
    less_arrs = [less_arr[0:proportion_count] for less_arr in less_arrs]

    retarrs = [np.concatenate ((less_arr, greater_arr)) for less_arr, greater_arr in zip(less_arrs, greater_arrs)]
    
    return retarrs

"""
Splits specified list of arrays in specified proportion
Args:
    arrs: list of arrays
    test_size: floating point value from 0 to 1 representing test dataset proportion
Returns:
    tuple of list of arrays
    first list is train dataset
    second is test dataset
"""
def train_test_split (arrs, test_size):
    arrs = shuffle_arrs (arrs)
    test_size_count = int ((1.0-test_size) * len(arrs[0]))
    train = [arr[0:test_size_count] for arr in arrs]
    test = [arr[test_size_count:] for arr in arrs]
    return train, test

"""
Loads datasets from CSV file, doesn't load images
Args:
    datasets: list of
        strings - dataset dir path or
        tuples - (dataset dir path, floating point proportion of dataset needed to be loaded)
        
    for example:
        ['dir/path', ('dir/path', 0.5)]
Returns:
    tuple of two arrays:
        steering wheel data array,
        camera image path array
"""
def load_datasets (datasets):
    all_steering = np.zeros ((0,))
    all_center = np.zeros ((0,))
    for dataset in datasets:
        dataset_file = ''
        dataset_size = 1
        if (isinstance(dataset, tuple)):
            dataset_file = dataset [0]
            dataset_size = dataset [1]
        else:
            dataset_file = dataset
        
        driving_log = genfromtxt (
            dataset_file + '/driving_log.csv',
            delimiter=',',
            skip_header=1,
            dtype=None)

        #center, left, right, steering, throttle, break, speed
        indices = range (len(driving_log))
        center, left, right, steering, throttle, breakvals, speed = zip (*driving_log)
        center = np.asarray (center)
        steering = np.asarray (steering)
        
        if (dataset_size < 1):
            arrs, not_needed = train_test_split ([steering, center], test_size=1-dataset_size)
            steering, center = arrs

        all_steering = np.concatenate([all_steering, steering])
        all_center = np.concatenate([
                all_center,
                np.core.defchararray.add(
                    dataset_file + '/IMG/',
                    np.asarray (
                            [ntpath.basename (path) for path in np.core.defchararray.decode(center)]
                        )
                )
            ])

    return all_steering, all_center

#loading dataset images
"""
Loades dataset images
Args:
    paths: arrays of image paths
Returns:
    numpy arrays of grayscaled, normalized images,
    pixel values are in range (-0.5, 0.5)
"""
def load_images (paths):
    dataset_images = []
    for path in paths:
        im = cv2.imread (path, cv2.IMREAD_GRAYSCALE)
        im = np.subtract(np.divide(np.array(im).astype(np.float32), 255.0), 0.5)
        dataset_images.append (im)
    return np.array (dataset_images)

offset = 0.22
Rows, Cols = 64, 64
def load_csv(csv_path,show=False):
    #csv_path = '../../../driving_log.csv'  # my data (fantastic graphic mode)
    center_db, left_db, right_db, steer_db = [], [], [], []
    
    # read csv file
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if float(row['steering']) != 0.0:
                center_db.append(row['center'])
                left_db.append(row['left'].strip())
                right_db.append(row['right'].strip())
                steer_db.append(float(row['steering']))
            else:
                prob = np.random.uniform()
                if prob <= 0.15:
                    center_db.append(row['center'])
                    left_db.append(row['left'].strip())
                    right_db.append(row['right'].strip())
                    steer_db.append(float(row['steering']))

    # shuffle a dataset
    center_db, left_db, right_db, steer_db = shuffle(center_db, left_db, right_db, steer_db)

    # split train & valid data
    img_train, img_valid, steer_train, steer_valid = train_test_split(center_db, steer_db, test_size=0.1, random_state=42)
    
    if show is True:
        plt.hist(steer_db, bins= 50, color= 'orange')
        plt.xlabel('steering value')
        plt.ylabel('counts')
        plt.show()
    else:
        return center_db,left_db, right_db,steer_db,img_valid,steer_valid





def select_img(center, left, right, steer, num, offsets=0.22):
    """
    randomly select among center, left, right images

    add ±0.22 to left, right steering angle.
    couldn't find exact left, right steering angle by using geometric method because we didn't have enough information.
    """
    rand = np.random.randint(3)

    if rand == 0:
        image, steering = cv2.imread(center[num]), steer[num]
    elif rand == 1:
        image, steering = cv2.imread(left[num]), steer[num] + offsets
    elif rand == 2:
        image, steering = cv2.imread(right[num]), steer[num] - offsets
    if abs(steering) > 1:
        steering = -1 if (steering < 0) else 1

    return image, steering

def valid_img(valid_image, valid_steer, num):
    """ using only center image for validation """
    steering = valid_steer[num]
    image = cv2.imread(valid_image[num])
    return image, steering

def crop_img(image):
   
    """ crop unnecessary parts """
    
    cropped_img = image[63:136, 0:319]
    
    resized_img = cv2.resize(cropped_img, (Cols,Rows))
    #resized_img = cv2.resize(cropped_img, (Cols,Rows), cv2.INTER_AREA)
    img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
    return resized_img

def shift_img(image, steer):
    """
    randomly shift image horizontally
    add proper steering angle to each image
    """
    max_shift = 55
    max_ang = 0.14  # ang_per_pixel = 0.0025

    rows, cols, _ = image.shape

    random_x = np.random.randint(-max_shift, max_shift + 1)
    dst_steer = steer + (random_x / max_shift) * max_ang
    if abs(dst_steer) > 1:
        dst_steer = -1 if (dst_steer < 0) else 1

    mat = np.float32([[1, 0, random_x], [0, 1, 0]])
    dst_img = cv2.warpAffine(image, mat, (cols, rows))
    return dst_img, dst_steer

def brightness_img(image):
    """
    randomly change brightness by converting Y value
    """
    br_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    coin = np.random.randint(2)
    if coin == 0:
        random_bright = 0.2 + np.random.uniform(0.2, 0.6)
        br_img[:, :, 2] = br_img[:, :, 2] * random_bright
    br_img = cv2.cvtColor(br_img, cv2.COLOR_HSV2RGB)
    return br_img

def generate_shadow(image, min_alpha=0.5, max_alpha = 0.75):
    """generate random shadow in random region"""

    top_x, bottom_x = np.random.randint(0, Cols, 2)
    coin = np.random.randint(2)
    rows, cols, _ = image.shape
    shadow_img = image.copy()
    if coin == 0:
        rand = np.random.randint(2)
        vertices = np.array([[(50, 65), (45, 0), (145, 0), (150, 65)]], dtype=np.int32)
        if rand == 0:
            vertices = np.array([[top_x, 0], [0, 0], [0, rows], [bottom_x, rows]], dtype=np.int32)
        elif rand == 1:
            vertices = np.array([[top_x, 0], [cols, 0], [cols, rows], [bottom_x, rows]], dtype=np.int32)
        mask = image.copy()
        channel_count = image.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (0,) * channel_count
        cv2.fillPoly(mask, [vertices], ignore_mask_color)
        rand_alpha = np.random.uniform(min_alpha, max_alpha)
        cv2.addWeighted(mask, rand_alpha, image, 1 - rand_alpha, 0., shadow_img)

    return shadow_img

def flip_img(image, steering):
    """ randomly flip image to gain right turn data (track1 is biaed in left turn) """
    flip_image = image.copy()
    flip_steering = steering
    num = np.random.randint(2)
    if num == 0:
        flip_image, flip_steering = cv2.flip(image, 1), -steering
    return flip_image, flip_steering



def generate_train(center, left, right, steer):
    
    """
    data augmentation
    transformed image & crop
    """

    num = np.random.randint(0, len(steer))
    # to avoid bias in straight angle
    #bal = True
    #while bal:
    #    num = np.random.randint(0, len(steer))
    #    check_steer = steer[num]
    #    if check_steer == 0:
    #        rand = np.random.uniform()
    #        if rand <= 0.25:
    #            bal = False
    #    else:
    #        bal = False

    image, steering = select_img(center, left, right, steer, num, offset)

    image, steering = shift_img(image, steering)
    image, steering = flip_img(image, steering)
    image = brightness_img(image)
    # image = generate_shadow(image)
    image = crop_img(image)
    return image, steering

def generate_valid(img_valid, steer_valid):
    """ generate validation set """
    img_set = np.zeros((len(img_valid), Rows, Cols, 3))
    steer_set = np.zeros(len(steer_valid))

    for i in range(len(img_valid)):
        img, steer = valid_img(img_valid, steer_valid, i)
        img_set[i] = crop_img(img)

        steer_set[i] = steer
    return img_set, steer_set

def generate_train_batch(center, left, right, steering, batch_size):
    """ compose training batch set """
    image_set = np.zeros((batch_size, Rows, Cols, 3))
    steering_set = np.zeros(batch_size)

    while 1:
        for i in range(batch_size):
            img, steer = generate_train(center, left, right, steering)
            image_set[i] = img
            steering_set[i] = steer
        yield image_set, steering_set


def saveModel(model,model_json,model_weights):
    #Save model
    #from keras.models import model_from_json
    #model_json = model.to_json()
    #with open("/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/model_final.json", "w") as json_file:
         #json_file.write(model_json)
    json_string = model.to_json()
    with open(model_json, 'w') as jfile:
         json.dump(json_string, jfile)
    model.save_weights(model_weights)
    #model.save_weights(model_weights, True)
    #model.save("/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/model_final.h5")
    print("Saved model to disk")



def Check_images_size(paths):
    new_path = os.path.join(paths, "IMG/", "*.jpg")
    for infile in glob.glob(new_path)[:2]:
       im = Image.open(infile)
       print(im.size, im.mode)
       # All images are 320x160

def load_csv_withPandas(paths):
    ## Link to Udacity's sample data
    
    os.chdir(paths)

    ## Link to my collected  data
    path_mydata = "/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/my_driving"

    # Import as a dataframe and plot steering
    df = pd.read_csv('driving_log.csv', header=0)
    df.columns = ["center_image", "left_image", "right_image", "steering", "throttle", "break", "speed"]
    df.drop(['throttle', 'break', 'speed'], axis = 1, inplace = True)

    import seaborn as sns
    sns.set(style="whitegrid", color_codes=True)
    sns.distplot(df['steering'], kde = False)

    print(len(df))


#defining augmentation of the dataset
"""
Image augmentation function.
It creates new image with
    - randomized brightness (-0.3, 0.3)
    - randomly partially occluded with 30
        black 25x25 px squares
    - very slightely randomly:
        - rotated (1 degree)
        - shifted (2px)
        - scaled (0.02)

Args:
    image: base image for generation new one
Returns:
    newly generatied image
"""
def augment_image (image):

    image = np.copy (image)
    
    (h, w) = image.shape[:2]
    
    #randomize brightness
    brightness = rand.uniform (-0.3, 0.3)
    image = np.add(image, brightness)
    
    #random squares
    rect_w = 25
    rect_h = 25
    rect_count = 30
    for i in range (rect_count):
        pt1 = (rand.randint (0, w), rand.randint (0, h))
        pt2 = (pt1[0] + rect_w, pt1[1] + rect_h)
        cv2.rectangle(image, pt1, pt2, (-0.5, -0.5, -0.5), -1)
    
    #rotation and scaling
    rot = 1
    scale = 0.02
    Mrot = cv2.getRotationMatrix2D((h/2,w/2),rand.uniform(-rot, rot), rand.uniform(1.0 - scale, 1.0 + scale))

    #affine transform and shifts
    pts1 = np.float32([[0,0],[w,0],[w,h]])
    a = 0
    shift = 2
    shiftx = rand.randint (-shift, shift);
    shifty = rand.randint (-shift, shift);
    pts2 = np.float32([[
                0 + rand.randint (-a, a) + shiftx,
                0 + rand.randint (-a, a) + shifty
            ],[
                w + rand.randint (-a, a) + shiftx,
                0 + rand.randint (-a, a) + shifty
            ],[
                w + rand.randint (-a, a) + shiftx,
                h + rand.randint (-a, a) + shifty
            ]])
    M = cv2.getAffineTransform(pts1,pts2)

    augmented = cv2.warpAffine(
            cv2.warpAffine (
                image
                , Mrot, (w, h)
            )
            , M, (w,h)
        )
    
    return augmented

"""
Augments image basing on input image with augment_image.
Also randomly flips image and steering wheel correspondingly.
Also adds normal noise (0, 0.005) to steering angle
Args:
    im: image
    steering: steering wheel angle
Returns:
    tuple:
        image,
        steering wheel
"""
def augment_record (im, steering):
    im = augment_image(im)
    if (rand.uniform (0, 1) > 0.5):
        im = cv2.flip (im, 1)
        steering = - steering
    steering = steering + np.random.normal (0, 0.005)
    return im, steering

"""
Grenerator for training samples
Args:
    images_arr: train dataset images
    steering_arr: train dataset steering
    batch_size: batch size
Returns:
    Only generated batch of samples, not includes original samples
"""
def augment_generator (images_arr, steering_arr, batch_size):
    last_index = len (images_arr) - 1
    while 1:
        batch_img = []
        batch_steering = []
        for i in range (batch_size):
            
            idx_img = rand.randint (0, last_index)
            im, steering = augment_record (images_arr [idx_img], steering_arr[idx_img])
            
            batch_img.append (im)
            batch_steering.append (steering)
            
        batch_img = np.asarray (batch_img)
        batch_steering = np.asarray (batch_steering)
        yield (batch_img, batch_steering)


"""
# Start with train generator shared in the class and add image augmentations
def train_generator_mode2(samples, batch_size=batch_size):
    num_samples = len(samples)
    while 1: # Loop forever so the generator never terminates
        from sklearn.utils import shuffle
        shuffle(samples)
        for offset in range(0, num_samples, batch_size):
            batch_samples = samples[offset:offset+batch_size]

            images = []
            angles = []
            # Read center, left and right images from a folder containing Udacity data and my data
            for batch_sample in batch_samples:
                center_name = '/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/data2/IMG/'+batch_sample[0].split('/')[-1]
                center_image = cv2.imread(center_name)
                center_image = cv2.cvtColor(center_image, cv2.COLOR_BGR2RGB)
                left_name = '/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/data2/IMG/'+batch_sample[1].split('/')[-1]
                left_image = cv2.imread(left_name)
                left_image = cv2.cvtColor(left_image, cv2.COLOR_BGR2RGB)
                right_name = '/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/data2/IMG/'+batch_sample[2].split('/')[-1]
                right_image = cv2.imread(right_name)
                right_image = cv2.cvtColor(right_image, cv2.COLOR_BGR2RGB)

                center_angle = float(batch_sample[3])

                # Apply correction for left and right steering
                correction = 0.20
                left_angle = center_angle + correction
                right_angle = center_angle - correction

                # Randomly include either center, left or right image
                num = random.random()
                if num <= 0.33:
                    select_image = center_image
                    select_angle = center_angle
                    images.append(select_image)
                    angles.append(select_angle)
                elif num>0.33 and num<=0.66:
                    select_image = left_image
                    select_angle = left_angle
                    images.append(select_image)
                    angles.append(select_angle)
                else:
                    select_image = right_image
                    select_angle = right_angle
                    images.append(select_image)
                    angles.append(select_angle)

                # Randomly horizontally flip selected images with 80% probability
                keep_prob = random.random()
                if keep_prob >0.20:
                    flip_image = np.fliplr(select_image)
                    flip_angle = -1*select_angle
                    images.append(flip_image)
                    angles.append(flip_angle)

                # Augment with images of different brightness
                # Randomly select a percent change
                change_pct = random.uniform(0.4, 1.2)

                # Change to HSV to change the brightness V
                hsv = cv2.cvtColor(select_image, cv2.COLOR_RGB2HSV)

                hsv[:, :, 2] = hsv[:, :, 2] * change_pct
                # Convert back to RGB and append

                bright_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                images.append(bright_img)
                angles.append(select_angle)

                ## Randomly shear image with 80% probability
                shear_prob = random.random()
                if shear_prob >=0.20:
                    shear_range = 40
                    rows, cols, ch = select_image.shape
                    dx = np.random.randint(-shear_range, shear_range + 1)
                    #    print('dx',dx)
                    random_point = [cols / 2 + dx, rows / 2]
                    pts1 = np.float32([[0, rows], [cols, rows], [cols / 2, rows / 2]])
                    pts2 = np.float32([[0, rows], [cols, rows], random_point])
                    dsteering = dx / (rows / 2) * 360 / (2 * np.pi * 25.0) / 10.0
                    M = cv2.getAffineTransform(pts1, pts2)
                    shear_image = cv2.warpAffine(center_image, M, (cols, rows), borderMode=1)
                    shear_angle = select_angle + dsteering
                    images.append(shear_image)
                    angles.append(shear_angle)

            # trim image to only see section with road
            X_train = np.array(images)
            y_train = np.array(angles)

            yield shuffle(X_train, y_train)

def valid_generator_mode2(samples, batch_size=batch_size):
        num_samples = len(samples)
        while 1:  # Loop forever so the generator never terminates
            from sklearn.utils import shuffle
            shuffle(samples)
            for offset in range(0, num_samples, batch_size):
                batch_samples = samples[offset:offset + batch_size]

                images = []
                angles = []

                #Validation generator only has center images and no augmentations
                for batch_sample in batch_samples:
                    center_name = '/home/animesh/Documents/CarND/CarND-Behavioral-Cloning-P3/data2/IMG/' + batch_sample[0].split('/')[-1]
                    center_image = cv2.imread(center_name)
                    center_image = cv2.cvtColor(center_image, cv2.COLOR_BGR2RGB)

                    center_angle = float(batch_sample[3])

                    images.append(center_image)
                    angles.append(center_angle)

                X_train = np.array(images)
                y_train = np.array(angles)

                yield shuffle(X_train, y_train)

# Function to resize image to 64x64
def resize_image(image):
    import tensorflow as tf
    return tf.image.resize_images(image,[64,64])

"""