import cv2
import time
from pathlib import Path
from tqdm.auto import tqdm
from mcpi.minecraft import Minecraft

from mcpi2 import logger
from mcpi2.constants import *
from mcpi2.utils.common import read_yaml



class ImageBuilder:
    """
    Class for building images in the Minecraft

    Attributes:
    - config (dict): Configuration settings.
    - image_height (int): Height at which the image is built.
    - max_image_size (int): Maximum size of each dimension of the image. In case of the bigger image, it will be downscaled.
    - colormap (str): Colormap to which the image will be converted (grayscale, redscale).
    - flip_colormap (bool): Whether to flip_colormap the colormap
    """

    def __init__(self, 
                 image_height: int = None,
                 max_image_size: int = None,
                 colormap: str = 'one_value.grayscale',
                 flip_colormap: bool = False):
        """
        Initializes ImageBuilder class
    
        Parameters:
        - image_height (int): Height at which the image is built.
        - max_image_size (int): Maximum size of each dimension of the image. In case of the bigger image, it will be downscaled.
        - colormap (str): Colormap to which the image will be converted (grayscale, redscale).
        - flip_colormap (bool): Whether to flip_colormap the colormap
        """

        self.config = read_yaml(CONFIG_FILE_PATH)['image']
        self.image_height, self.max_image_size, self.colormap = self.validate(image_height, max_image_size, colormap)
        self.flip_colormap = flip_colormap
        

    def validate(self,        
                 image_height: int,
                 max_image_size: int,
                 colormap: str):
        """
        Validates input parameters
    
        Parameters:
        - image_height (int): Height at which the image is built.
        - max_image_size (int): Maximum size of each dimension of the image. In case of the bigger image, it will be downscaled.
        - colormap (str): Colormap to which the image will be converted (grayscale, redscale).
    
        Returns:
        - image_height (int): Height at which the image is built.
        - max_image_size (int): Maximum size of each dimension of the image. In case of the bigger image, it will be downscaled.
        - colormap (str): Colormap to which the image will be converted (grayscale, redscale).
        """
        
        if image_height == None:
            image_height = self.config['height']
        elif type(image_height) != int:
            logger.error(f'image_height must be int, not {type(image_height)}')
            raise TypeError(f'image_height must be int, not {type(image_height)}')
        
        if max_image_size == None:
            max_image_size = self.config['size']['default']
        elif type(max_image_size) != int:
            logger.error(f'max_image_size must be int, not {type(max_image_size)}')
            raise TypeError(f'max_image_size must be int, not {type(max_image_size)}')
        elif (max_image_size < self.config['size']['min']) or (max_image_size > self.config['size']['max']):
            logger.error(f"max_image_size must be between {self.config['size']['min']} and {self.config['size']['max']}, while {max_image_size} is specified")
            raise ValueError(f"max_image_size must be between {self.config['size']['min']} and {self.config['size']['max']}, while {max_image_size} is specified")
    
        if colormap == None:
            colormap = self.config['default_colormap']
        elif type(colormap) != str:
            logger.error(f'colormap must be str, not {type(colormap)}')
            raise TypeError(f'colormap must be str, not {type(colormap)}')
        elif colormap not in self.config['blocks'].keys():
            logger.error(f"colormap must be one of the following options: {', '.join(list(self.config['blocks'].keys()))}. Not {colormap}")
            raise ValueError(f"colormap must be one of the following options: {', '.join(list(self.config['blocks'].keys()))}. Not {colormap}")
    
        return image_height, max_image_size, colormap


    def build(self,
              mc: Minecraft,
              path_to_image: Path):
        """
        Reads the input image and then builds it in the Minecraft

        Parameters:
        - mc (Minecraft): Objectto interact with the Minecraft client
        - path_to_image (Path): Path to the image
        """

        # reading the image
        image = cv2.imread(path_to_image)
        logger.info('Image has been loaded')

        # downscaling the image in case it is bigger along any dimension
        old_shape = image.shape
        if (image.shape[1] > image.shape[0]) and (image.shape[1] > self.max_image_size):
            image = cv2.resize(image, (self.max_image_size, int(image.shape[0] / image.shape[1] * self.max_image_size)), interpolation=cv2.INTER_AREA)
            logger.info(f'Image has been downscaled from {old_shape} to {image.shape}')
        elif (image.shape[0] >= image.shape[1]) and (image.shape[0] > MAX_SIZE):
            image = cv2.resize(image, (int(image.shape[1] / image.shape[0] * self.max_image_size), self.max_image_size), interpolation=cv2.INTER_AREA)
            logger.info(f'Image has been downscaled from {old_shape} to {image.shape}')
        else:
            logger.info(f'Image has not been downscaled as it is already approriate with shape {image.shape}')

        if self.colormap.split('.')[0] == 'one_value':
            # Chagning colormap
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            logger.info(f'Colormap has been changed')
        
            # Converting values to the index of blocks which will encode each pixel
            section_size = 256/len(self.config['blocks'][self.colormap])         
            image = (image // section_size).astype(int)
        
        logger.info(f'Image has been preprocessed')

        # Getting the current position of the player
        x, y, z = mc.player.getTilePos()

        # Building the image row by row
        x_start = x
        for row in tqdm(image):
            for number in row:
                if not self.flip_colormap:
                    mc.setBlock(x, self.image_height, z, 
                                self.config['blocks'][self.colormap][number][0], 
                                self.config['blocks'][self.colormap][number][1])
                else:
                    mc.setBlock(x, self.image_height, z, 
                                self.config['blocks'][self.colormap][len(self.config['blocks'][self.colormap])-1-number][0], 
                                self.config['blocks'][self.colormap][len(self.config['blocks'][self.colormap])-1-number][1])                    
                x += 1
            z += 1
            x = x_start
            time.sleep(self.config['building_time_delay'])