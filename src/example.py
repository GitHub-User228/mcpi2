from mcpi.minecraft import Minecraft
from mcpi2.constants import *
from mcpi2.f.image import ImageBuilder



PROJECT_DIR = os.path.abspath(os.path.join(os.path.join(PACKAGE_DIR, os.pardir), os.pardir))
IMAGES_DIR = os.path.join(PROJECT_DIR, 'images')



mc = Minecraft.create(address='172.21.64.1', port=4711)
builder = ImageBuilder(max_image_size=512, colormap='one_value.grayscale', flip_colormap=False)
builder.build(mc, path_to_image=os.path.join(IMAGES_DIR, 'fox.jpg'))