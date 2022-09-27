from collections import OrderedDict

orig_data = OrderedDict([('q_1', 45), ('q_2', 425)])

print(orig_data)
data = list(orig_data.items())

for obj in orig_data.items():
    print(obj[1])