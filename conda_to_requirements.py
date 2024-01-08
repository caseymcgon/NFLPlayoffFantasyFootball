## converts the active conda enironment into a requirments.txt file & prepares it for streamlit

import os
os.system("pip freeze > requirements.txt")

with open('requirements.txt', 'r') as f:
    lines = f.readlines()

with open('requirements.txt', 'w') as f:
    for line in lines:
        ## remove anything after an @
        line = line.split('@')[0].strip()  # Split the line at the '@' sign and keep only the part before it    
        f.write(line + '\n')
