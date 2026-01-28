Prerequest: Python 3.9 or above, with the following libraries: numpy, pillow, opencv-python and moviepy
Plateform: Windows, macOS, Linux, or any other system supports python
Program has been suceessfully tested on: macOS V15.7.3, Pycharm 2024.1.7 (Community Edition), Python 3.9

Instruction to run "image2txt.py"
1. put any photo in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff"} format under the same folder of "image2txt.py"
2. run the program
3. Two files will be generated, one is "pic.txt" file which is the one to be uploaded to display control MCU, the other is "pic_debug.txt" which is reformatted so that researcher could easier check the file content.

Instruction to run "video2BinFiles.py"
1. put any video in "mp4" format under the same folder of "video2BinFiles.py". If you are trying your own video, you need to rename it to "video.mp4"
2. run the program
3. Eight files will be generated, six of them are in ".bin" format which will be uploaded six display control MCUs controlling corresponding six display zones of the screen.
   ".pcm" file will also be uploaded and played as the audio part of the video. ".wav" file is for researcher to check the output audio.
