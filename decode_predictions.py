import numpy as np
def decode_predictions(scores, geometry):
	(numRows, numCols) = scores.shape[2:4]
	rects = []
	confidences = []
	for y in range(0, numRows):
		scoresData = scores[0, 0, y]
		xData0 = geometry[0, 0, y]
		xData1 = geometry[0, 1, y]
		xData2 = geometry[0, 2, y]
		xData3 = geometry[0, 3, y]
		anglesData = geometry[0, 4, y]
		for x in range(0, numCols):
			if scoresData[x] < 0.5:
				continue
			(offsetX, offsetY) = (x * 4.0, y * 4.0)
			angle = anglesData[x]
			cos = np.cos(angle)
			sin = np.sin(angle)
			h = xData0[x] + xData2[x]
			w = xData1[x] + xData3[x]
			endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
			endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
			startX = int(endX - w)
			startY = int(endY - h)
			rects.append((startX, startY, endX, endY))
			confidences.append(scoresData[x])
	return (rects, confidences)