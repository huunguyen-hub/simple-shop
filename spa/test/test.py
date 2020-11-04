g1 = ["U", "V", "W"]
g2 = ['X', 'Y', 'Z']
g3 = ["A", "B", "C"]
g4 = ['1', '2']
matrix = [g1, g2, g3]
items = {}  #
# explicit for loops
max_combined = 0
for i in range(len(matrix)):
    if max_combined == 0:
        max_combined = len(matrix[i])
    else:
        max_combined = max_combined * len(matrix[i])
print("max items={}".format(max_combined))
items = {}
for i in range(max_combined):
    item = {str(i): []}
    items.update(item)
print(matrix)
max_record = 0
static_pointer = 0
dynamic_pointer = 0
row_first = True
item_fist = True


def double_replace(result, sta_pointer, dyn_pointer, cur, rep):
    for x in range(sta_pointer):
        list_item = result[str(x)]
        new_list = list_item[:]  # copying a list using slicing
        if rep in new_list and cur not in new_list:
            new_list.remove(rep)
            new_list.append(cur)
        result[str(dyn_pointer)] = new_list
        dyn_pointer += 1
    return result


for i in range(len(matrix)):
    if row_first:
        row_first = False
        for j in range(len(matrix[i])):
            # print('i={},j={}'.format(i, j))
            current = matrix[i][j]
            _item = [current]
            items[str(j)] = _item
    else:
        _first = None
        for j in range(len(matrix[i])):
            # print('i={},j={}'.format(i, j))
            current = matrix[i][j]
            if item_fist:
                item_fist = False
                _first = matrix[i][j]
                for p in range(static_pointer):
                    _item = items[str(p)]
                    if current not in _item:
                        _item.append(current)
                    items[str(p)] = _item
            else:
                dynamic_pointer = j * static_pointer
                print('call i={},j={} and static={} dyn={}'.format(i, j, static_pointer, dynamic_pointer))
                if current != _first:
                    items = double_replace(items, static_pointer, dynamic_pointer, current, _first)
            dynamic_pointer = j * static_pointer if j > 0 else static_pointer
        item_fist = True
    static_pointer = static_pointer * len(matrix[i]) if static_pointer > 0 else len(matrix[i])
    # print('i={},j={} and static={} dyn={}'.format(i, j, static_pointer, dynamic_pointer))

print(items)
