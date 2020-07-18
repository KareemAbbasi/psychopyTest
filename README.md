# Cognitive Experiment

This is a cognitive experiment that is programmed as a programming test.

## Usage

To use, you need to install psychopy and numpy.
They can be downloaded using the package manager [pip](https://pip.pypa.io/en/stable/)

```bash
pip install numpy
pip install psychopy
```

To run the program use the following command:

```bash
python main.py -o OUTPUT_FILE
```
where ```OUTPUT_FILE``` is the name used for the final log file. Enter the name without extension as the program will create a ```OUTPUT_FILE.csv``` file at the end of it's run.

The default configurations will run the experiment on 20 images and 20 sounds. These can be changed. 
You can use the following to get more details:
```bash
python main.py -h
```
