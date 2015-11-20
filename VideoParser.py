# import the necessary packages
import sys, os, imutils, cv, cv2, math, glob, csv
import numpy as np


class FrameParser: 
	def __init__(self, threshold=0.85):
		self.threshold = threshold

	#Returns a list of columns with a description of the sprites in the passed in frame Image
	def GetFrameDescription(self, frameNumber, frame, sprites, overlapThreshold =4, minDist = 4 ):		
		columns = []

		for sprite in sprites:
			#Pattern matching right here
			result = cv2.matchTemplate(sprite[0], frame, cv2.TM_CCOEFF_NORMED)#Change cv2.TM_CCOEFF_NORMED for more accurate but slower results
			(h, w) = sprite[0].shape[:2]
			#Get only the max values (those above the threshold) that represent a local maximum
			maxVals  = MaxLocalVals(result, w, h, self.threshold)
			for pt in maxVals:
				#Whether or not to add this to the list of columns
				addIt = True
				#The potential new column to add
				column = [str(frameNumber), sprite[1], str(pt[0]), str(pt[1]), str(w), str(h), str(result[pt[1]][pt[0]])]
				#The list of columns that this one forces out
				toRemove = []

				#Iterate through all current columns and ensure that no column subsumes this one and that this one subsumes no others
				for c in columns:
					#Feel free to add this back in, though it'll slow things down a bit it's good for when some sprites contain others
					'''
					#Check if this column is inside one of the others
					if not c in toRemove:
						if OverlapAmount(c, column)>=overlapThreshold:
							# c is in column, remove c
							cScore = float(c[6])
							if cScore<result[pt[1]][pt[0]]:
								toRemove.append(c)
							else:
								addIt = False
								break 
					'''
					#Ensure that there isn't something better in this region that has a higher score
					if addIt and not c in toRemove:
						if abs(int(c[2])-int(column[2]))<=minDist and abs(int(c[3]) - int(column[3]) )<=minDist:
							c6 = float(c[6])
							if c6<result[pt[1]][pt[0]]:
								toRemove.append(c)
							else:
								addIt = False
								break

				#Removes those that need removing
				for r in toRemove:
					columns.remove(r)

				#Add those that need adding
				if addIt:
					columns.append(column)

		return columns


#Find the highest scoring top left corner within a range (in this case half width and half height)
def MaxLocalVals(result, width, height, threshold):
	loc = np.where( result >= threshold)
	locPoints = []


	for pt in zip(*loc[::-1]):
		maxVal = result[pt[1]][pt[0]]
		#New point to potentially add
		maxPnt = pt
		toRemove = []

		#Ensure that you have the best local points
		for pt2 in locPoints:
			if maxVal<result[pt2[1]][pt2[0]] and (abs(pt2[0]-pt[0])<width/2.0 and abs(pt2[1]-pt[1])<height/2.0):#Is this point already in locPoints and in range and is it better?
				maxPnt = pt2
			elif maxPnt==pt and (abs(pt2[0]-pt[0])<width/2.0 and abs(pt2[1]-pt[1])<height/2.0):#Inverse, Does this point beat out something in locPoints?
				toRemove.append(pt2)

		for pt2 in toRemove:
			locPoints.remove(pt2)
		if maxPnt== pt:
			locPoints.append(pt)

	return locPoints

#Check the amount of overlapping pixels between these two sprites, represented as columns
def OverlapAmount(column1, column2, printIt = False):

	#Rectangle defined by column1
	rectAX1 = int(column1[2])
	rectAX2 = rectAX1 + int(column1[4])
	rectAY1 = int(column1[3])
	rectAY2 = rectAY1 + int(column1[5])

	#Rectangle defined by column2
	rectBX1 = int(column2[2])
	rectBX2 = rectBX1 + int(column2[4])
	rectBY1 = int(column2[3])
	rectBY2 = rectBY1 + int(column2[5])

	l1 = (rectAX1,rectAY1)
	r1 = (rectAX2,rectAY2)
	l2 = (rectBX1,rectBY1)
	r2 = (rectBX2,rectBY2)

	SI = max(0, max(r1[0], r2[0]) -min(l1[0], l2[0]))*max(0, max(r1[1], r2[1]) -min(l1[1], l2[1]))
	# width1*height1 + width2*height2
	SU = ((r1[0]-l1[0])*(r1[1]-l1[1]))+((r2[0]-l2[0])*(r2[1]-l2[1]))-SI
	if SU==0:
		return 0

	return float(SI) / float(SU)


if __name__ == '__main__':
	FFMPEG_BIN = "ffmpeg" # Use on Linux ans Mac OS
	#FFMPEG_BIN = "ffmpeg.exe" # Use on Windows


	#Example call: python VideoParser.py Gameplay.mp4 sprites 1
	video = sys.argv[1]
	spritesDirectory = sys.argv[2]
	framesPerSecond = sys.argv[3]

	#The folder that the frame images will end up in
	folder = "./frames/"	
	if not os.path.exists(folder):
		os.makedirs(folder)

	#Run the parser to generate the frame images
	os.system(FFMPEG_BIN+ " -i "+video+" -r "+framesPerSecond+" "+folder+"image-%08d.png")#" -vf scale="+widthOfFrame+":"+heightOfFrame+
	
	sprites = []
	directory = "./"+spritesDirectory+"/"
	for filename in glob.glob(directory+"*.png"):
		img_rgb = cv2.imread(filename)
		sprite_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)#Gray is faster to match
		splits = filename.split("/")
		spritename = splits[len(splits)-1]
		sprites.append((sprite_gray, spritename))

	#Initialize Frame Parser
	fp = FrameParser()

	target = open(folder+"frameDescriptions.csv","wb")
	writer = csv.writer(target)
	column = ["frame", "spritename", "x", "y", "w", "h", "confidence"]
	writer.writerow(column)

	for frameFile in glob.glob(folder+"*.png"):
		print "Frames: "+str(frameFile)
		frame = cv2.imread(frameFile)
		frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		splits =frameFile.split("image-")
		frameNumber = int(splits[len(splits)-1][:-4])

		columns = fp.GetFrameDescription(frameNumber,frame_gray,sprites)

		for c in columns:
			writer.writerow(c)
