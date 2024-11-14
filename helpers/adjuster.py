from helpers.weather_codes import weather_codes
import pprint
from random import random

new_codes = {}

for code in weather_codes:
    day_array = weather_codes[code][0]
    if len(day_array) == 1:
        new_codes[code] = weather_codes[code]
        continue
    night_array = weather_codes[code][1]
    new_day_array = []
    
    t_count = 0
    for r,g,b,t in night_array:
        t_count+=t
        if code < 60:
            random_b_adj = int(100 + random() * 100)
            random_g_adj = int(40 + random() * 60)
            random_r_adj = int(random() * 40)
        if code > 60:
            random_b_adj = int(100 + random() * 155)
            random_g_adj = int(20 + random() * 150)
            random_r_adj = int(random() * 50)

        new_day_array.append((random_r_adj, g+random_g_adj, random_b_adj, t))

    print(code, t_count)
    new_codes[code] = (new_day_array, night_array)


print(len(new_codes))
'''
f = open("/Users/jaredgantt/nanoControl/new_codes.py", "w")
f.write("new_codes = ")
f.close()

with open('/Users/jaredgantt/nanoControl/new_codes.py', 'a') as file:
    pprint.pprint(new_codes, file)

'''