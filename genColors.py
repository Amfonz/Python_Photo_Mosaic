from PIL import Image
from pathlib import Path
#the idea is that with a bunch of base color images if our photo mosaic program
#can accurately pick the right color than the alogroithm works




def create_colors():
    #we are not looking to generate the full spectrum just get good coverage
    #for testing purposes
    x=0
    
    for r in range(0,255,50):
        for g in range(0,255,50):
            for b in range(0,255,50):
                p=Path('./colors/im_%d.png' %(x))
                im = Image.new('RGB',(10,10),(r,g,b))
                im.save(p)
                x+=1
  


if __name__ == '__main__':
    create_colors()
'''
    im = Image.new('RGB',(10,10),(10,10,10))
    im.show()
    p = Path('./colors/df.png')
    im.save(p)
'''
