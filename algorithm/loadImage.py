from pathlib import Path
import cv2

def load_image(image_path):
	my_file = Path(image_path)
	if my_file.is_file():
		return(cv2.imread(image_path))
	else:
		return None