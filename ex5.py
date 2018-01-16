my_name = "Zed A. Shaw"
my_age = 36 #not a lie
my_height = 73 #inches
my_weight = 175 #lbs
my_eyes = 'Blue'
my_teeth = 'White'
my_hair = 'Brown'

# f-strings (sting literal replacement introduced in python 3.6.
print("Let talk about {}".format(my_name))
print(f"He's {my_height} inches tall")
print(f"He's {my_weight} poubds heavy")
print(f"He's got {my_eyes} eyes and {my_hair} hair")

total = my_age + my_height + my_weight
print(f"If I add {my_age} + {my_height} + {my_weight} = {total}.")
