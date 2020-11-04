from main.const import IMAGE_SIZES_INDEX

for size in IMAGE_SIZES_INDEX:
    print(size, IMAGE_SIZES_INDEX[size])

img_ratio = float(640) / 480
(x, y) = (640, 480) if img_ratio >= float(1) else (480, 640)

print(x, y)
print(float(1))