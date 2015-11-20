import sys, glob, os
sys.path.append('/usr/local/lib/python2.7/site-packages')
import PIL
from PIL import Image

if __name__ == '__main__':
	#Read in arguments
	spriteDirectory = "./"+sys.argv[1]+"/"
	resizeRatioX = float(sys.argv[2])
	resizeRatioY = float(sys.argv[2])

	if len(sys.argv)>3:
		resizeRatioX = float(sys.argv[2])
		resizeRatioY = float(sys.argv[3])

	#Create sprite directory
	resizedSpriteDirectory = spriteDirectory+"resizedSprites/"

	if not os.path.exists(resizedSpriteDirectory):
		os.makedirs(resizedSpriteDirectory)

	#Go through each sprite, resize and 
	for filename in glob.glob(spriteDirectory+"*.png"):
		sprite = Image.open(filename)
		#Get the base sprite size
		(width, height) = sprite.size
		#Get new dimensions
		newWidth= int(round(width*resizeRatioX))
		newHeight= int(round(height*resizeRatioY))

		#Create resized sprite
		resizedSprite=sprite.resize((newWidth, newHeight), PIL.Image.ANTIALIAS)

		#Create resized sprite name
		splits = filename.split("/")
		resizedSpriteName = resizedSpriteDirectory+splits[len(splits)-1]
		resizedSprite.save(resizedSpriteName)		




