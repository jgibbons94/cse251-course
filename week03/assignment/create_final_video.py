"""
CSE251
Program to create final video from images
"""

import os
import platform

def main():
    # the folder "processed" must exist
    if not os.path.exists('processed'):
        print('\nERROR: the folder "processed" doesn\'t exist\n')
        return 

    # Use one variable for all the args passed to ffmpeg.
    # This way, it's easier to maintain.
    args = '-y -i processed/image%3d.png -f ipod final.mp4'
    executable = r'ffmpeg ' if platform.system() in ['Linux', 'Windows'] else r'./ffmpeg'
    command = f'{executable} {args}'

    os.system(command)

    print('\nThe video file final.mp4 has been created\n')

main()
