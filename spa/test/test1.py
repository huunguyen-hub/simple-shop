colors = ["red", "green", "blue", "purple"]
ratios = [0.2, 0.3, 0.1, 0.4]
print(enumerate(colors))
for i, color in enumerate(colors):
    ratio = ratios[i]
    print("{} {}% {}".format(i, ratio * 100, color))
