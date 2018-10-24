from sklearn.cluster import KMeans
from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(image_path):
	my_file = Path(image_path)
	if my_file.is_file():
		return(cv2.imread(image_path))
	else:
		return None

def main():
	image = load_image('test_dataset/ODESSA.png')
	#print(image.shape)
	if image is not None:
		(image_clustered,clusters) = clustering(image, 4)
		masks = [np.zeros(image.shape) for i in range(clusters.shape[0])]
		print(clusters)
		for i in range(clusters.shape[0]):
			masks[i] = cv2.inRange(image_clustered, clusters[i], clusters[i])
		for i in range(clusters.shape[0]):
			cv2.imshow("sample", masks[i])
			cv2.waitKey()
			cv2.destroyAllWindows()

		#plt.figure(2)
		#plt.imshow(image)
		#plt.show()
	else:
		print("File is not exist")
	
def recreate_image(codebook, labels, w, h):
    """Recreate the (compressed) image from the code book & labels"""
    d = codebook.shape[1]
    image = np.zeros((w, h, d))
    label_idx = 0
    for i in range(w):
        for j in range(h):
            image[i][j] = codebook[labels[label_idx]]
            label_idx += 1
    return image

def clustering(image, clusters_count):
	w, h, d = original_shape = tuple(image.shape)
	assert d == 3
	image = np.array(image, dtype=np.float64)
	image_array = np.reshape(image, (w * h, d))
	kmeans = KMeans(n_clusters=clusters_count, random_state=0).fit(image_array)
	labels = kmeans.predict(image_array)
	image = recreate_image(kmeans.cluster_centers_, labels, w, h)
	image = np.array(image, np.uint8)
	return(image,np.array(kmeans.cluster_centers_,np.uint8))
	
if __name__ == "__main__":
	main()
