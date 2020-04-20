import cv2


class RGBHistogram:
    def __init__(self, bins, nb_splits):
        # store the number of bins the histogram will use
        self.bins = bins
        # store the number of splits to be performed on the image
        self.nb_splits = nb_splits

    def calc_hist(self, image):
        hist = cv2.calcHist(
            [image], [0, 1, 2], None, self.bins, [0, 256, 0, 256, 0, 256]
        )
        cv2.normalize(hist, hist)
        # 3D histogram as a flattened array
        hist.flatten()

        return hist

    def describe(self, image):
        width, height, _ = image.shape
        block_w = width // self.nb_splits
        block_h = height // self.nb_splits
        hists = []
        hist = self.calc_hist(image)
        # store the image hitogram
        hists.append(hist)

        # compute the blocks histograms
        for i in range(0, width, block_w):
            for j in range(0, height, block_h):
                w = min([i+block_w, width])
                h = min([j+block_h, height])
                block = image[i:i+w, j:j+h, :]
                hists.append(self.calc_hist(block))

        return hists
