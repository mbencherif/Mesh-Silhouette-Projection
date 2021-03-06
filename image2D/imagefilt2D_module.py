"""
image_filt.py

Module containing image processing filters that could be useful for 
transforming the image before airway detection

Created on Mon Nov 21 15:09:07 2011

@author: Benjamin Irving

"""

import scipy.ndimage as nd
import numpy as np
import dicom
import pickle
import matplotlib.pyplot as plt
# -*- coding: utf-8 -*-

class Image:
    
    def __init__(self, I):
        self.I=I - I.min();
        self.conv=0;
        self.intmax=0.0 # max of int
        self.doubmin=0.0
        
    def __call__(self):
        return self.I

    def __str__(self):
        return "This is an image"       
        
    def doub_norm(self):
        """ Convert from int16 to double??? """
        
        if self.conv is 0:
            self.intmax=self.I.max()
            self.conv=1;
        
        
        self.I=np.double(self.I)   
        self.I=(self.I + self.doubmin) / self.intmax 

        
    def int16rec(self):
        """ convert back to int16"""
        
        if self.conv is 0:
            print "Cannot be converted back unless originally converted"
        else:
            self.doubmin=self.I.min()
            self.I=(self.I - self.doubmin) * self.intmax
            self.I=np.uint16(self.I)
            
    def plot(self, figure_num=1):
        plt.figure(figure_num)
        plt.imshow(self.I, cmap=plt.cm.gray)
            
        
        
    def crop_border(self):
        """ 
        Crop border voxels that match [0,0] pixel.
        Used because Lodox images seem to have a very large border
        """
        tc=self.I[0,0]
        iscorner= self.I!=tc
        
        a=iscorner.max(axis=0)
        #nonzer returns a tuple for coordinates so have to unpack
        anon=a.nonzero()[0]
        
        b=iscorner.max(axis=1)
        bnon=b.nonzero()[0]
        
        #crop borders containing zero voxel values
        self.I=self.I[bnon.min():bnon.max(), anon.min():anon.max()]
        
     
    @property
    def Igrad_mag(self):
        self._Igrad_mag, _,_=sobel_gradient(self.I)
        return self._Igrad_mag

class XrayImage(Image):
    """
    Extension of the image class to take dicoms
    """
    
    def __init__(self, folder1, file1):
        self.folder1=folder1
        self.file1=file1
        Imxray1=dicom.read_file(self.folder1 + self.file1 + ".dcm")

        
        Image.__init__(self, Imxray1.pixel_array)        
 
    def select_points(self, x=1, append1=""):
	    try:                
		apfile=open(self.folder1 + self.file1 + "_align" + append1 + ".pkl", 'rb')
		xxyy=pickle.load(apfile)
		apfile.close()
		self.xx=xxyy[:,0]
		self.yy=xxyy[:,1]
	    except:
		print "Error: Alignment points file doesn't exist"
		 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
## Other functions that are not part of the class ##                  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def local_norm(Im, s=4.0):
    """
    Local normalisation filter of schilham2003msn (preprocessing step)
    """    
    
    G=nd.gaussian_filter #gaussian filter
    
    #equation outlined by schilam et al. This appears to be wrong.
    #Im_out=(Im-G(Im,s))/((G(Im**2,s)-G(Im,s)**2)**0.5) ) 
    #correct local normalisation method. denominator is an estimate of standard deviation around a pixel. 
    #correction of longs formula for the denominator
    Im_out=(Im-G(Im,s))/((G((Im-G(Im,s))**2, s) )**0.5) 
    #Im_out=np.nan_to_num(Im_out)
    
    Im_out=(Im_out-Im_out.min())/(Im_out.max()-Im_out.min())
    
    print Im_out[0,0]
    
    return Im_out
    
def unsharp_mask(Im, s=4.0, alpha=10):
    """
    Create a sharpened image by adding the difference between the gaussian blur. 
    """
    
    G=nd.gaussian_filter
    mask=Im-G(Im, s)
    Im_out=Im+alpha*mask
    
    return Im_out
    
def diff_of_gauss(Im, s1=5.0):
    s2=s1*1.6
    G=nd.gaussian_filter
    Img1=G(Im, s1)
    Img2=G(Im, s2)
    
    Im_out=Img1-Img2
    return Im_out
    
    
def simple_gradient(Im):
    g1=np.array([-0.5, 0, 0.5])
    
    Imx=nd.convolve1d(Im, g1, axis=0)
    Imy=nd.convolve1d(Im, g1, axis=1)
    
    ImMag=(Imx**2 +Imy**2)**0.5
    
    return ImMag, Imx, Imy
    
def sobel_gradient(Im):
    Imy=nd.sobel(Im, axis=0)
    Imx=nd.sobel(Im, axis=1)
    
    ImMag=(Imx**2 +Imy**2)**0.5
    
    return ImMag, Imx, Imy
    

