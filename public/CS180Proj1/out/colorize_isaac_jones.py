# CS194-26 (CS294-26): Project 1 starter Python code

# these are just some suggested libraries
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import sys

# name of the input file
imname = sys.argv[1] if len(sys.argv) > 1 else "cathedral.jpg"

alignType = 'pyramid'

# read in the image as grayscale (the glass plate scan is stacked grayscale)
im = cv.imread(imname, cv.IMREAD_GRAYSCALE)

# convert to float in [0,1] (might want to do this later on to save memory)
im = im.astype(np.float32) / 255.0
    
# compute the height of each part (just 1/3 of total)
height = int(np.floor(im.shape[0] / 3.0))

# separate color channels
b = im[:height]
g = im[height: 2*height]
r = im[2*height: 3*height]

def cosineScore(im1, im2):
    #This is effectively equivalent to NCC scoring, just with img2 size normalization. This makes debugging easier.
    img1 = im1[:].copy()
    img2 = im2[:].copy()
    img1 = img1.reshape(-1)
    img2 = img2.reshape(-1)
    img1-=np.mean(img1)
    img2-=np.mean(img2)
    img1/=np.std(img1)
    img2/=np.std(img2)
    return np.dot(img1, img2)/np.dot(img2, img2)

'''
def clip(im, x, y):
    out = im[:,:].copy()
    if y >= 0:
        out = out[y:,:]
    else:
        out = out[:y,:]

    if x >= 0:
        out = out[:,x:]
    else:
        out = out[:,:x]

    return out
'''
    

def align(im1, im2, startX=-3, startY=-3, endX=3, endY=3, method='bruteforce'):
    '''
    Align im1 to match im2.
    '''

    #print(im1.shape, im2.shape)

    assert im1.shape == im2.shape, "different sized images"

    bestX = 0
    bestY = 0

    if method == 'pyramid':
        maxSize = 200
        greaterSize = max(im2.shape)
        cutRate = 2
        print(greaterSize)
        if greaterSize > maxSize:

            #Take a smaller version of the image
            im1Resized = cv.resize(im1, None, fx=1/cutRate, fy=1/cutRate, interpolation=cv.INTER_AREA)
            im2Resized = cv.resize(im2, None, fx=1/cutRate, fy=1/cutRate, interpolation=cv.INTER_AREA)
            print(im1Resized.shape)

            #Find the best alignment for that smaller version of the image
            matched, x, y = align(im1Resized, im2Resized, startX, startY, endX, endY, method='pyramid')

            #shift appropriately by the best shift times the cut rate
            edited = np.roll(im1, y*cutRate, 0)
            edited = np.roll(edited, x*cutRate, 1)

            #get rid of the borders temporarily for close inspection; de noising
            absx, absy = (abs(x)+1)*3, (abs(y)+1)*3
            edited = edited[absy*cutRate:-absy*cutRate, absx*cutRate:-absx*cutRate]
            im2 = im2[absy*cutRate:-absy*cutRate, absx*cutRate:-absx*cutRate].copy()
            
            print("shifted by ", x*cutRate, y*cutRate)

            #Now that the image is roughly close, do a finer analysis with the full resolution
            _, finalx, finaly = align(edited, im2, startX, startY, endX, endY, method='bruteforce')
            finaledited = np.roll(im1, y*cutRate+finaly, 0)
            finaledited = np.roll(finaledited, x*cutRate+finalx, 1)
            print("returning to higher loop: ", x*cutRate+finalx, y*cutRate+finaly)
            return (finaledited, x*cutRate+finalx, y*cutRate+finaly)
        else:
            return align(im1, im2, method='bruteforce')


    elif method == 'bruteforce':

        #This is the base case. Simply run through every possibility and see which is best.
        xAlign = startX
        yAlign = startY
        bestScore = -1
        #start from the top left.
        while xAlign <= endX:
            yAlign = startY
            while yAlign <=endY:

                edited2 = im2
                #shift
                edited1 = np.roll(im1, yAlign, 0)
                edited1 = np.roll(edited1, xAlign, 1)
                #and then just lop off the borders when checking, which tend to be noisy
                cropX = (endX-startX)*3
                cropY = (endY-startY)*3
                edited1 = edited1[cropY:-cropY, cropX:-cropX]
                edited2 = edited2[cropY:-cropY, cropX:-cropX]
                #This scores whether a particular alignment is "good" or not.
                score = cosineScore(edited1, edited2)
                print(xAlign, yAlign, score)
                if score > bestScore:
                    #Keep track of the best alignment and score
                    bestX = xAlign
                    bestY = yAlign
                    bestScore = score
                yAlign+=1
            xAlign+=1

        #Finally roll the original by the discovered best alignment and return
        edited = np.roll(im1, bestY, 0)
        edited = np.roll(edited, bestX, 1)
        print(bestX, bestY)
        
        return (edited, bestX, bestY)


    

# align the images
# functions that might be useful for aligning the images include:
# np.roll, np.sum, sk.transform.rescale (for multiscale)

ag, gx, gy = align(g, b,method=alignType)
ar, rx, ry = align(r, b,method=alignType)

#ag=g
#ar=r

print (gx, gy, rx, ry)



# create a color image
im_out = np.dstack([ar, ag, b])

means = np.mean(im_out, (0, 1))
OVERALL = np.mean(means)

multipliers = OVERALL/means

im_out[:, :]*=multipliers
means = np.mean(im_out, (0, 1))
#print(means)
im_out = np.clip(im_out, 0, 1)

# display the image using matplotlib (expects RGB)
plt.figure(figsize=(8, 8))
plt.imshow(im_out)
plt.title('Colorized')
plt.axis('off')
plt.show()

# prepare for OpenCV saving/display (expects BGR uint8)
out_uint8 = np.clip(im_out * 255.0, 0, 255).astype(np.uint8)
out_bgr = cv.cvtColor(out_uint8, cv.COLOR_RGB2BGR)

# save the image
fname = './out_fname.jpg'
cv.imwrite(fname, out_bgr)

