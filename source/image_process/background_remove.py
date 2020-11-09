import os
import subprocess
import cv2
import numpy as np
from matplotlib import pyplot as plt

temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')

BLUR = 21
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 200
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10
MASK_COLOR = (0.0,0.0,1.0) # In BGR format


class BackgroundRemoval(object):
    def __init__(self, image_file=None):
        super(BackgroundRemoval, self).__init__()

        self.image_file = image_file
        self.img = None
        self.color_mask = False
        self.magick_exe = r'A:/tools/ImageMagick-7.0.10-Q16-HDRI/magick.exe'
        self._initialize()

    def _initialize(self):
        pass

    def masked_bg(self, colour=False):
        self.color_mask = colour
        self.img = cv2.imread(self.image_file)
        self.edge_dection()

    def white_bg(self):
        output_file = os.path.join(temp_dir, 'white_bg_img.png')
        cmd = "{} convert {} -transparent white {}".format(self.magick_exe, self.image_file, output_file)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        return output_file

    def black_bg(self):
        output_file = os.path.join(temp_dir, 'black_bg_img.png')
        cmd = "{} convert {} -fuzz 20% -transparent white {}".format(self.magick_exe, self.image_file, output_file)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        return output_file

    def edge_dection(self):
        gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
        edges = cv2.dilate(edges, None)
        edges = cv2.erode(edges, None)
        rets_list = cv2.RETR_LIST
        chain = cv2.CHAIN_APPROX_NONE
        contour_info = []
        contours, _ = cv2.findContours(edges, rets_list, chain)
        # Previously, for a previous version of cv2, this line was:
        #  contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        # Thanks to notes from commenters, I've updated the code but left this note
        for c in contours:
            contour_info.append((
                c,
                cv2.isContourConvex(c),
                cv2.contourArea(c),
            ))
        contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
        max_contour = contour_info[0]
        self.mask = np.zeros(edges.shape)
        cv2.fillConvexPoly(self.mask, max_contour[0], (255))
        self.masking()

    def masking(self):
        mask = cv2.dilate(self.mask, None, iterations=MASK_DILATE_ITER)
        mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
        mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
        mask_stack = np.dstack([mask] * 3)
        mask_stack = mask_stack.astype('float32') / 255.0  # Use float matrices,
        img = self.img.astype('float32') / 255.0  # for easy blending

        print ("masking color", self.color_mask)
        if self.color_mask:
            masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR) # Blend
            masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit
            # cv2.imshow('img', masked)                                   # Display
            # cv2.waitKey()
            output_file = os.path.join(temp_dir, 'temp_color_img.png')
            cv2.imwrite(output_file, masked)
            print (">>>ouyrtttt", output_file)                             # Save
            return output_file
        else:
            c_red, c_green, c_blue = cv2.split(img)
            img_a = cv2.merge((c_red, c_green, c_blue, mask.astype('float32') / 255.0))
            # plt.imshow(img_a)
            # plt.show()
            output_file = os.path.join(temp_dir, 'temp_grey_img.png')
            cv2.imwrite(output_file, img_a * 255)
            # plt.imsave('girl_2.png', img_a)
            return output_file



# a = BackgroundRemoval(image_file=r"A:\dwonload\baground_remove_demo.jpg", colour=True)



