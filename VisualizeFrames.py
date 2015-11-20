import csv, sys, os, copy, glob, cv2
sys.path.append('/usr/local/lib/python2.7/site-packages')
from PIL import Image

class FrameObject:
	def __init__(self, name, positionX, positionY, width, height):
		self.name = name
		self.x = positionX
		self.y = positionY
		self.width = width
		self.height = height

if __name__ == '__main__':
	spriteDirectory = sys.argv[1]
	frameCSV = sys.argv[2]
	translatedFramesDirectory = "./"+sys.argv[3]

	if not os.path.exists(translatedFramesDirectory):
		os.makedirs(translatedFramesDirectory)

	#STEP 1: Grab the sprites
	sprites = {}

	directory = "./"+spriteDirectory+"/"
	for filename in glob.glob(directory+"*.png"):
		img_rgb = Image.open(filename)
		keep = img_rgb.copy()

		splits = filename.split("/")
		spritename = splits[len(splits)-1]
		sprites[spritename] = keep
		img_rgb.close()#Ensure that we don't hit python's "too many files open" error

	#STEP 2: This section grabs the frame objects per frame as just strings
	source = open(frameCSV,"rb")
	reader = csv.reader(source)

	readLine = False#skip the first frame
	currFrame = 0
	prevFrame = 0
	gameplayVals = {}

	for row in reader:
		if readLine:
			currFrame = int(row[0])
			if not currFrame==prevFrame:
				gameplayVals.setdefault(currFrame, [])
				prevFrame = currFrame
			
			objName = str(row[1])
			gameplayVals[currFrame].append(FrameObject(objName,int(row[2]),int(row[3]), int(row[4]), int(row[5])))
			prevFrame = currFrame

		readLine=True

	#STEP 3: Print the frames
	for translatedFrame in gameplayVals.keys():
		print "Translating Frame: "+str(translatedFrame)
		filenameStr = translatedFramesDirectory+"/"+str(translatedFrame)+".png"

		#Find max points of image to use as height and width
		maxX = 0
		maxY = 0
		for frameObject in gameplayVals[translatedFrame]:
			if frameObject.x+frameObject.width>maxX:
				maxX = frameObject.x+frameObject.width
			if frameObject.y+frameObject.height>maxY:
				maxY = frameObject.y+frameObject.height


		#Make the frame image
		img = Image.new('RGB', (int(maxX), int(maxY)), "rgb(91, 147, 251)")#CHANGE THIS TO CHANGE THE DEFAULT BACKGROUND COLOR
		pixels = img.load()
		#Iterate through every object in this frame and draw it
		for o in gameplayVals[translatedFrame]:
			if o.name in sprites.keys():
				sprite = sprites[o.name]
				pix = sprite.load()
				(width, height) = sprite.size
				for x in range(0, int(width)):
					for y in range(0, int(height)):
						xIndex = int(o.x)+x
						yIndex = int(o.y)+y
						r = int((pix[x,y][0]))
						g = int((pix[x,y][1]))
						b = int((pix[x,y][2]))
						newVal = (r,g,b)
						
						pixels[xIndex,yIndex]=newVal
		img.save(filenameStr)
