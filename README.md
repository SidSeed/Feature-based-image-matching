# Feature-based-image-matching
Using a distorted image, fiding all similar images from a dataset of images.
## Table of contents
* [General info](#general-info)
* [Screenshots](#screenshots)
* [Requirements](#requirements)
* [Setup](#setup)
* [Running a test](#running)
* [Implementation](#implementation)
* [Status](#status)
* [Inspiration](#inspiration)
* [Contact](#contact)

## General info
Detection of similar images in a set of images, where one of them is the distorted (cropped, rotated or with enhanced saturation). This is achieved by dividing the images and extracting a set of features then performing a block to block matching.
## Screenshots
![Example screenshot](./img/image-matching.png)
![Example screenshot](./img/indexer.png)
## Requirements
* Python - version 2.7 or later
* Opencv
* Numpy
* PyQt5


## Setup
Numpy:
```
pip install numpy
```
Opencv:
```
pip install opencv-python
```
PyQt5
```
pip install pyqt5
```
## Running
#### Clone
Clone this repo to your local machine using https://github.com/SidSeed/Feature-based-image-matching.git
#### Test
```
python searcher_gui.py
```
## Implementation
This project was developed in four steps:

__1. Defining the descriptor:__  
We’re using a 3D color histogram in the RGB color space with 8 bins per red, green, and blue channel.  A histogram represents the distribution of colors in an image. It can be visualized as a graph (or plot) that gives a high-level intuition of the intensity (pixel value) distribution. We are going to assume an RGB color space.
#### code
```diff
import cv2

class RGBHistogram:
    def __init__(self, bins, nb_splits):
+        # store the number of bins the histogram will use
        self.bins = bins
+        # store the number of splits to be performed on the image
        self.nb_splits = nb_splits

    def calc_hist(self, image):
        hist = cv2.calcHist(
            [image], [0, 1, 2], None, self.bins, [0, 256, 0, 256, 0, 256]
        )
        cv2.normalize(hist, hist)
+        # 3D histogram
        hist.flatten()

        return hist

    def describe(self, image):
        width, height, _ = image.shape
        block_w = width // self.nb_splits
        block_h = height // self.nb_splits
        hists = []
        hist = self.calc_hist(image)
+        # store the image hitogram
        hists.append(hist)

+        # compute the blocks histograms
        for i in range(0, width, block_w):
            for j in range(0, height, block_h):
                w = min([i+block_w, width])
                h = min([j+block_h, height])
                block = image[i:i+w, j:j+h, :]
                hists.append(self.calc_hist(block))

        return hists

```
__2. Indexing the dataset:__  

The second thing we are going to do is to index the 25 images of our dataset. Indexing is the process of quantifying our dataset by using an image descriptor (Listed above) to extract features from each image and storing the resulting features for later use.
As every image is divided to many blocks depending on the size of the image,
That means we will loop over our 25 images dataset, extract a 3D RGB histogram from every block of those images.
The output of an image descriptor is a features vector, an abstraction of the image itself. 
We applying the descriptor to each block of the image in our dataset, extracting a set of features and saving them in a file called ‘index.pkl’.
#### code
```diff
def index_imgs(self):
        self.index_images.setEnabled(False)
        if not self.images:
            QtGui.QMessageBox.critical(
                self, 'Selection error', 'No image selected'
            )
            return

        self.overlay.show()
        index = {}

+        # variable of our frature extractor a 3D RGB histogram with
+        # 8 bins per channel
        desc = RGBHistogram([8, 8, 8], 5)

+        # use glob to grab the image paths and loop over them
        for imagePath in self.images:

+            # load the image, extract feature using our RGB histogram
+            # and update the index file
            image = cv2.imread(imagePath)
            features = desc.describe(image)
            index[imagePath] = features

+        # Writing our index file to disk

        filename = 'index.pkl'
        with open(filename, 'wb') as handle:
            pickle.dump(index, handle)
        self.overlay.hide()
        QtGui.QMessageBox.information(
            self, 'Indexing complete', '%s images indexed. Indexed file saves as %s' % (
                len(self.images), filename
            )
        )


```
__3. Define the metric similarity:__

We’re using the chi-squared distance with a cross-bin chi^2-like normalization.  Every feature vectors can be compared using a distance metric. A distance metric is used to determine how “similar” images are by examining the distance between feature vectors taken from our dataset images and the features of every block of our image query. 
#### code
```diff
+ # compute the chi-squared distance
        hist_sum = np.sum(
            [((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)]
        )
        d = 0.5 * hist_sum

+        # return the chi-squared distance
        return d

```
__4. Searching:__

To perform the search, We took our image query which we divided to blocks, apply the descriptor to every block, compute the distance of the first block of the image query with all blocks of other images in the dataset,and then ask for the distance metric to rank how similar the images are to our image query. At the end sort the results via similarity.
#### code
```diff
def search(self, query_features):
+        # initialize our dictionary of results
        results = {}

+        # loop over the index
        for (k, features) in self.index.items():
            
            scores = []
            for hist in features:
                score = np.amax(
                    [
                        self.chi2_distance(hist, query_hist)
                        for query_hist in query_features
                    ]
                )
                scores.append(score)
            d = np.sum(scores) / len(scores)

            
            results[k] = d

        
        results = sorted([(v, k) for (k, v) in results.items()])

+        # return our results
        return results
```

## Status
Project is:  _finished_
## Inspiration
Project inspired by image recognition subject. 
## Contact
Created by [@sidseed] - feel free to contact me!
