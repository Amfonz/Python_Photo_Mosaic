from PIL import Image
from functools import reduce
from pathlib import Path
from bisect import bisect_left
from math import floor, ceil
'''
todo:  tile calculation is wrong


    gui for file choosing
      allow choice for resulting file type
      error handling


      change to class
      implement change that uses desired choice for saving (file name and type)



gal_map
rgb_sum
rgb_tup
gal_map_keys

'''

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Gallery Image Pre processing



'''''

class MosaicGenerator:
    def __init__(self,target,gallery,save_name,tile_size,process_label,status_label):
        self.target_path = target
        self.gallery = gallery
        self.tile_size = tile_size
        self.process_label = process_label
        self.status_label = status_label
        self.save_name = save_name


    def generate_mosaic(self):
        '''

        :return: error message as string if there is one otherwise empty string
        '''


        #process the gallery first
        self.process_label.set("processing gallery ...")
        [gal_map_keys,gal_map] = self.process_gallery()
        self.process_label.set("Gallery Processed")
        try:
            target = Image.open(Path(self.target_path))

        except IOError:
            return "target could not be found or is not an image"

        if self.tile_size < 1:
            return "tile size must be greater than or equal to 1"

        mosaic = Image.new('RGB',target.size)
        #4 loops
        # outer loops to jump entire tiles and inner loop to loop over tiles
        #
        #
        #
        tiles = ceil(mosaic.size[0]/self.tile_size) * ceil(mosaic.size[1]/self.tile_size) - 1
        tile = 0
        self.process_label.set("inserting images...")
        height = 0
        while height < mosaic.size[1]:
            #looping down the rows of tiles
            width = 0
            while width < mosaic.size[0]:
                #looping across tiles in rows
                i = height
                r = g = b = 0
                self.status_label.set("processing tile {:.0f} of {:.0f}".format(tile,tiles))
                while i < height + self.tile_size and i < mosaic.size[1]:
                    #looping down rows of pixels in a tile
                    j = width
                    while j < width + self.tile_size and j < mosaic.size[0]:
                        #looping across pixels in rows of a tile
                        pix = target.getpixel((j,i))
                        r += pix[0]
                        g += pix[1]
                        b += pix[2]
                        j += 1
                    i += 1
                r = round(r/(self.tile_size**2),2)
                g = round(g/(self.tile_size**2),2)
                b = round(b/(self.tile_size**2),2)
                replacement = self.get_tile_replacement(r+g+b,(r,g,b),gal_map_keys,gal_map)
                self.insert_image(mosaic,replacement,(width,height,width+self.tile_size,height+self.tile_size))
                width+=self.tile_size
                tile+=1
            height+=self.tile_size
        try:
            print(tile)
            print((mosaic.size[0]*mosaic.size[1])/self.tile_size**2)
            print((mosaic.size[0]*mosaic.size[1])/tile)
            mosaic.save(self.save_name)

        except (ValueError, IOError):
            return "The mosaic could not be saved"
        self.process_label.set("Finished")
        self.status_label.set("")
        return ""


    def avg_img_colors(self,img):
        #:params an image object
        #returns a 3-tuple of the images average (R,G,B ) values

        #average the rgb values of every pixel in the image
        #return (R,G,B) where each is an average
        height, width = img.height, img.width
        r,g,b = 0, 0, 0
        for i in range(width):
            for j in range(height):
                ptup = img.getpixel((i,j))
                r += ptup[0]
                g += ptup[1]
                b += ptup[2]
        r /= width * height
        g /= width * height
        b /= width * height
        return (round(r,2),round(g,2),round(b,2))




    def process_gallery(self):
        #:Params path to a folder of images
        #:returns sorted list of keys and a dict mapping rgb sums to images

        #loop through gallery open images get the rgb and sum them
        #map resultant sums to lists of file paths
        gal_map = {}
        pos_path = Path(self.gallery)
        for f in pos_path.iterdir():
            try:
                temp_im = Image.open(f)
                self.status_label.set("processing: " + f.name)
                #create a new image, sum its rgb values and add it to the map
                temp_im = temp_im.convert('RGB')
                temp_im = temp_im.resize((self.tile_size,self.tile_size))
                rgb_tup = self.avg_img_colors(temp_im)
                rgb_sum = round(reduce(lambda x,y : x+y, rgb_tup),2)
                if rgb_sum in gal_map:
                    #append f to RGBSUMS[rgb_sum]
                    gal_map[rgb_sum].append((f,rgb_tup))
                else: #create a new entry
                    gal_map[rgb_sum] = [(f,rgb_tup)]
                temp_im.close()
            except IOError:
                pass
        gal_map_keys = sorted(gal_map)
        return [gal_map_keys,gal_map]


    ''''
    /Gallery Pre processing

    '''''''''''''''''''''''''''''''''''''''''''''''''''
    '''''''''''''''''''''''''''''''''''''''''''''
    Tile replacement & comparison methods

    process is as follows

    1. get the sum rgb of a tile and the average (R,G,B) tuple
    2. find the right image to replace it
        a. find the right key into the dict using the rgb sum
        b. if multiple images to a key sort out the best one using the tile image difference
        c. return the right image and place into new image

    '''''

    def tile_image_difference(self,rgb1,rgb2):
        #:params two tuples of (R,G,B) values (these are average values)
        #one is from a tile of the target and the other is from the gallery
        #:returns int - the sum of the differences ie R-R, G-G Summed


        #rgb 1&2 are 3-tuples of rgb values one from an image and one from a tile
        #of the target image to be replaced

        #take average (r,g,b) of tile and image and reduce it to a single value
        #get the sum of the differences from a tuple which
        #is the result of taking the abs - from the corresponding values in the
        #params

        #returns a single int
        return reduce(lambda x,y : x+y,tuple(map(lambda a,b : abs(a-b),rgb1,rgb2)))

    def search_for_index(self,tile_rgb_sum,gal_map_keys):
        #:params the sum of the tiles avg R,G,B values used to index the map
        #:returns the index to the images closest in total rgb values to the tile

        #search for a key to the map that matches to supplied tile_rgb
        #left bisect to find a match or closest match

        key_index = bisect_left(gal_map_keys,tile_rgb_sum)
        if key_index == len(gal_map_keys): #case where the sum is greater than any key we have
            return gal_map_keys[key_index-1]
        elif key_index == 0:#smaller or exactly 0 take the first one
            return gal_map_keys[0]
        elif gal_map_keys[key_index] == tile_rgb_sum: #exact match
            return tile_rgb_sum
        else:
            #we need to look at the values to the right and left and see which diff
            # is smaller
            if abs(gal_map_keys[key_index] - tile_rgb_sum) <= abs(gal_map_keys[key_index -1 ] - tile_rgb_sum):
                return gal_map_keys[key_index]
            else:
                return gal_map_keys[key_index-1]

    def get_tile_replacement(self,tile_rgb_sum,tile_rgb,gal_map_keys,image_dict):
        '''
        :params rgb sum of tile,rgb tuple form tile, gal_map_keys from gallery, map of gallery
        :returns an image path to be placed in the tiles place from the gallery
        '''
        key = self.search_for_index(tile_rgb_sum,gal_map_keys)
        if len(image_dict[key]) == 1:
            return image_dict[key][0][0]
        else:
            best = image_dict[key][0][0]
            best_diff = self.tile_image_difference(image_dict[key][0][1],tile_rgb)
            for tup in image_dict[key]:
                curr = self.tile_image_difference(tup[1],tile_rgb)
                if curr < best_diff:
                    best = tup[0]
                    best_diff = curr

            return best




    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''
        Image insertion

    '''

    def insert_image(self,mosaic,img_path,coords):
        '''

        :param mosaic: the photomosaic the image is inserting into
        :param img_path: path to the iamge to be inserted
        :param coordsw: the coordinates to insert the image into (4 tuple)
        :return: nothing
        '''

        inserting_img = Image.open(img_path)
        inserting_img = inserting_img.resize((self.tile_size,self.tile_size))
        mosaic.paste(inserting_img,coords)
        inserting_img.close()























def test_process_gallery():
    a = process_gallery('./colors')
    print(a)

def test_image_replacement():
    print(tile_image_difference((3,4,6),(5,3,7)))
    a = process_gallery('./')
    print(search_for_index(100,a[0]))

#test_process_gallery()
#test_image_replacement()