# import the necessary packages
import numpy as np


class Searcher:
    def __init__(self, index):
        # store our index of images
        self.index = index

    def search(self, query_features):
        # initialize our dictionary of results
        results = {}

        # loop over the index
        for (k, features) in self.index.items():
            # compute the chi-squared distance between the histograms of
            # the features in our index and our query features -- 
      
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

            # now that we have the mean score between the two feature
            # vectors, we can udpate the results dictionary -- the
            # key is the current image ID in the index and the
            # value is the mean score we just computed, representing
            # how 'similar' the image in the index is to our query
            results[k] = d

        # sort our results, so that the smaller distances, the
        # more relevant images are at the front of the list
        results = sorted([(v, k) for (k, v) in results.items()])

        # return our results
        return results

    def chi2_distance(self, histA, histB, eps=1e-10):
        # compute the chi-squared distance
        hist_sum = np.sum(
            [((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)]
        )
        d = 0.5 * hist_sum

        # return the chi-squared distance
        return d
