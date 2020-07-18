# Cognitive Experiment

This is a cognitive experiment that is programmed as a programming test.

## Usage

To use, you need to install psychopy and numpy.
They can be downloaded using the package manager [pip](https://pip.pypa.io/en/stable/)

```bash
pip install numpy
pip install psychopy
```

To run the program use the following command. Make sure that the file ```main.py``` is in the same directory as the folder ```images``` which contains the images of the experiment, or you can specify the path for the images as shown below. 

```bash
python main.py -o OUTPUT_FILE
```
where ```OUTPUT_FILE``` is the name used for the final log file. Enter the name without extension as the program will create a ```OUTPUT_FILE.csv``` file at the end of it's run.

The default configurations will run the experiment on 20 images and 20 sounds. These can be changed. 
You can use the following to get more details:
```bash
python main.py -h
```

## Classes
### DataLogger
The data logger records the data of the experiment in two ways:
1. Writes to a csv file named ```OUTPUT_FILE.csv```, where ```OUTPUT_FILE``` can be changed by the user.
The data in this file is made from two columns. The first one is the name of the event and the second is the time of the event (counted since the beginning of the experiment).
2. Sends data to a parallel port. This is optional and works if you use the flag -pp 
```
python main.py -o OUTPUT_FILE -pp
``` 
You can also change the parallel port address by using -a 
```
python main.py -o OUTPUT_FILE -pp -a 0x0378
```

### ExperimentSounds
Responsible for the sounds played during the experiment. When using the default configurations, it will play a sound with the frequency 440Hz 15 times and the sound with the frequency 500Hz 5 times. Each sound will be played for 0.2 seconds.

You can change the frequencies and the number of times each one should be played. For example:
```bash
python main.py -o OUTPUT_FILE -f 440 500 660 880 -s 6 3 7 4
```
This will play the frequency 440Hz six times, 500Hz three times, 660Hz seven times and 880Hz four times.

### ExperimentImages
Generates the list of images that will be used in the experiment. The default images are in  ```images/```. This path can be changed using 
```bash
python main.py -o OUTPUT_FILE -i NEW_IMAGES_PATH
```
