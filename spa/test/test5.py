IMAGE_SIZES_W = {'big': (640, 480), 'mid': (320, 240), 'sm': (32, 24)}
IMAGE_SIZES_H = {'hbig': (480, 640), 'hmid': (240, 320), 'hsm': (24, 32)}
IMAGE_SIZES_INDEX = {**IMAGE_SIZES_W, **IMAGE_SIZES_H}
print(IMAGE_SIZES_INDEX)

IMG_SIZES_W = {(640, 480), (320, 240), (32, 24)}
IMG_SIZES_H = {(480, 640), (240, 320), (24, 32)}
IMAGE_SIZES = {*IMG_SIZES_W, *IMG_SIZES_H}
print(IMAGE_SIZES)

IMG_EXT_WITH_DOT = {'.jpg', '.jpeg', '.png', '.gif'}
IMG_EXT_NO_DOT = {ext.replace('.', '') for ext in IMG_EXT_WITH_DOT}
print(IMG_EXT_NO_DOT, type(IMG_EXT_NO_DOT))
