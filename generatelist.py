import sys
import os

imageDir = os.path.abspath(sys.argv[1])

totalImages = (int(sys.argv[2]) + 1)

initfiles = os.listdir(imageDir)

files = []

if totalImages == -1:
    totalImages = len(initfiles)
    
for i in xrange(1, totalImages):
    path = imageDir + "/" + initfiles[i]
    files.append(path)



i = 0
data = []
for jpgFilePath in files:
    resid = "fsa.4aa"
    prevIndex = "fsa4324"# if (i == 0) else data[i - 1][0]
    itemId = "item-" + str(i)
    id2use = itemId
    callstr = "idk-anymore"
    callnum = "50532"
    metadataPath = jpgFilePath + ".json"
    furl = resid
    s = (str(i + 1) + "#" + resid + "#" + prevIndex + "#" +  itemId + "#" +
        id2use + "#" + callstr + "#" + callnum + "#" + jpgFilePath + "#" +
        metadataPath + "#" + furl)
    data.append(s)
    i += 1

listFile = open(sys.argv[3], "w")
listFile.write("\n".join(data))
