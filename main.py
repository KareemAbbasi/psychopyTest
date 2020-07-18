"""

    File name: main.py
    Author: Kareem Abbasi
    Date created: 17/07/2020
    Python Version: 3.7
    E-mail: kareem.abbasi@mail.huji.ac.il

"""

from psychopy import prefs, visual, core, event, parallel
from random import uniform, sample
from enum import Enum
import numpy as np
import os
import argparse

prefs.hardware['audioLib'] = ['ptb']

from psychopy import sound  # import some libraries from PsychoPy

SOUND_DELAY_MIN = 50  # ms
SOUND_DELAY_MAX = 150  # ms
PARALLEL_ADDRESS = 0x0378

data_log = []

main_clock = core.Clock()


class ParallelData(Enum):
    FIXTURE_BEGIN = 2,
    FIXTURE_END = 3,
    IMAGE_BEGIN = 4,
    IMAGE_END = 5,
    USER_REACTION = 6,
    SOUND_START = 7,
    SOUND_END = 8


class DataLogger:
    """
    A class that records the data. Writes to an csv file and if wanted sends to parallel port.
    """

    def __init__(self, file_name="data", with_pp=False, pp_address=0x0378):
        self.file_name = file_name
        self.log = []

        self.with_pp = with_pp
        self.pp_address = pp_address

        if self.with_pp:
            self.port = parallel.ParallelPort(address=self.pp_address)

        self.dataFile = open(file_name + '.csv', 'w')
        self.dataFile.write("{},{}\n".format("Event", "Time"))

    def write_log_to_file(self):
        for l in self.log:
            self.dataFile.write("{},{}\n".format(l[0], l[1]))

        self.dataFile.close()

    def record_data(self, log_event, pp_data):
        self.log.append(log_event)
        if self.with_pp:
            self.port.setData(pp_data)


data_logger = DataLogger()


class ExperimentSounds:
    """
    Contains the frequencies that will be played and plays them according to the number of repetitions specified for
    each one.
    """

    def __init__(self, freqs=[440, 500], repetitions=[15, 5], duration=0.2):
        self._freqs = freqs
        self._repetitions = repetitions
        self._original_reps = repetitions
        self._duration = duration

    def set_duration(self, duration):
        """
        Set the duration of the sound.
        :param duration:
        :return:
        """
        self._duration = duration

    def play_sound(self, window: visual.Window):
        """
        Uniformly choses a frequency to play according to the number of repetitions for each one and plays it.
        :param window:
        :return:
        """
        total_repetitions = sum(self._repetitions)
        if total_repetitions == 0:
            self._repetitions = self._original_reps
            total_repetitions = sum(self._repetitions)

        probs = [float(rep) / total_repetitions for rep in self._repetitions]
        sound_index = np.random.choice(range(len(self._freqs)), p=probs)
        window.flip()
        new_sound = sound.Sound(self._freqs[sound_index], secs=self._duration)

        data_logger.record_data(['Play sound', main_clock.getTime()], ParallelData.SOUND_START)

        new_sound.play()
        data_logger.record_data(['Sound end', main_clock.getTime()], ParallelData.SOUND_START)

        window.flip()
        self._repetitions[sound_index] -= 1


class ExperimentImages:
    """
    A class to get the images used in the experiment.
    """

    def __init__(self, trials=20, path='images/'):
        self._path = path
        self._images = set()
        self.num_images = 0
        self.trials = trials
        self._get_images()
        self.counter = 0
        self.with_repetitions = False

    def _get_images(self):
        """
        Gets all the images from self.path
        :return:
        """
        for r, d, f in os.walk(self._path):
            for file in f:
                if "jpg" in file or "png" in file:
                    self._images.add(os.path.join(r, file))
        self.num_images = len(self._images)
        self.with_repetitions = self.trials > self.num_images

    def change_images_directory(self, directory_path):
        """Can be used to change the directory of the images used."""
        self._path = directory_path
        self._get_images()

    def chose_image(self):
        """
        Uniformly chooses an image to be used without repetitions.
        :return:
        """

        if len(self._images) <= 0 and self.with_repetitions:
            self._get_images()

        if len(self._images) > 0:
            choice = sample(self._images, 1)[0]
            self.remove_image(choice)
            self.counter += 1
            print(self.counter)
            return choice

        else:
            return None

    def add_image(self, image_path):
        """
        Adds the image from the path to the list of images that can be used.
        :param image_path:
        :return:
        """
        self._images.add(image_path)

    def remove_image(self, image_path):
        """
        Removes an image with the specified path from the list of images that can be used.
        :param image_path:
        :return:
        """
        if image_path in self._images:
            self._images.remove(image_path)


class MainWindow:
    """
    The class that runs the experiment.
    """

    def __init__(self, images, sounds, trials=20, fixation_time=0.1):
        self.my_win = visual.Window([800, 600], monitor="testMonitor", units="deg")
        self.fixation = visual.GratingStim(win=self.my_win, mask="cross", size=0.5, pos=[0, 0], sf=0, rgb=-1)
        self.images: ExperimentImages = images
        self.sounds: ExperimentSounds = sounds
        self.fixation_time = fixation_time
        self.trials = trials
        self.counter = 0

    def get_waiting_time(self):
        return uniform(SOUND_DELAY_MIN, SOUND_DELAY_MAX)

    def main_loop(self):
        image_name = self.images.chose_image()
        if image_name is not None:
            img = visual.ImageStim(
                win=self.my_win,
                image=image_name,
                units="pix"
            )

            size_x = img.size[0]
            size_y = img.size[1]

            new_x = self.my_win.size[0] * 0.35
            new_y = (new_x / size_x) * size_y

            img.size = [new_x, new_y]

            clock = core.Clock()

            data_logger.record_data(['Fixation time', main_clock.getTime()], ParallelData.FIXTURE_BEGIN)
            # data_log.append(['Fixation time', main_clock.getTime()])
            # port.setData(ParallelData.FIXTURE_BEGIN)

            while clock.getTime() < self.fixation_time:
                # print(clock.getTime())
                self.fixation.draw()
                self.my_win.flip()

            data_logger.record_data(['Fixation end', main_clock.getTime()], ParallelData.FIXTURE_END)

            # port.setData(ParallelData.FIXTURE_END)

            clock.reset()

            data_logger.record_data(['Image start', main_clock.getTime()], ParallelData.IMAGE_BEGIN)
            # data_log.append(['Image time', main_clock.getTime()])
            # port.setData(ParallelData.IMAGE_BEGIN)

            while clock.getTime() < 0.4:
                img.draw()
                self.my_win.flip()
                if len(event.getKeys()) > 0:
                    self.counter += 1
                    data_logger.record_data(['Reaction time', main_clock.getTime()], ParallelData.USER_REACTION)
                    # data_log.append(['Reaction time', main_clock.getTime()])
                    print("clicked something" + str(self.counter))
                event.clearEvents()

            data_logger.record_data(['Image end', main_clock.getTime()], ParallelData.IMAGE_END)
            # port.setData(ParallelData.IMAGE_END)

            self.my_win.flip()

            clock.reset()
            while clock.getTime() < self.get_waiting_time() / 1000:
                continue
            self.my_win.flip()
            self.sounds.play_sound(self.my_win)
            self.my_win.flip()
            return True
        return False

    def start(self):
        while True:
            text = visual.TextStim(self.my_win, "Press any key to start")
            text.draw()
            self.my_win.flip()
            if len(event.getKeys()) > 0:
                break

        main_clock.reset()
        for i in range(self.trials):
            self.main_loop()

        while True:
            text = visual.TextStim(self.my_win, "Press any key to exit")
            text.draw()
            self.my_win.flip()
            if len(event.getKeys()) > 0:
                break

        self.my_win.close()


def write_data(data_file):
    for l in data_log:
        data_file.write("{},{}\n".format(l[0], l[1]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cognition experiment...")
    parser.add_argument("-i", "--images", help="Path of the images directory. [Default: \"images/\"]",
                        default="images/", metavar="")
    parser.add_argument("-t", "--trials", type=int, help="Number of trials. [Default: 20]", default=20, metavar="")
    parser.add_argument("-o", "--outputName", help="Name of the output file.", required=True, metavar="")
    parser.add_argument("-f", "--freqs", type=int, nargs='+', help="The frequencies of the sounds.", metavar="")
    parser.add_argument("-s", "--soundsRepetitions", type=int, nargs='+',
                        help="Number of times each frequency should be repeated", metavar="")
    parser.add_argument("-d", "--soundDuration", type=float, help="The duration of the sound played [in seconds]",
                        metavar="")
    parser.add_argument("-D", "--soundDelay", type=int, nargs=2,
                        help="The delay between the images and the sound in milliseconds, minimum delay value then "
                             "maximum delay value.",
                        metavar="")
    parser.add_argument("-pp", "--withParallelPort", action="store_true",
                        help="Use this if you want to use the parallel port.")
    parser.add_argument("-a", "--parallelPortAddress", type=int, help="Address of the parallel port to be used.",
                        metavar="")

    args = parser.parse_args()

    sounds = ExperimentSounds()

    if args.freqs is not None:
        if len(args.soundsRepetitions) != len(args.freqs):
            raise Exception("Please enter how many times each sound should be repeated.")
        else:
            sounds = ExperimentSounds(args.freqs, args.soundsRepetitions)

    if args.soundsRepetitions is not None:
        if len(args.soundsRepetitions) != len(args.freqs):
            raise Exception("Please make sure you have the same number of frequencies match the number of repetitions.")
        else:
            sounds = ExperimentSounds(args.freqs, args.soundsRepetitions)

    if args.soundDuration is not None:
        sounds.set_duration(args.soundDuration)

    if args.soundDelay is not None:
        SOUND_DELAY_MIN = args.soundDelay[0]
        SOUND_DELAY_MAX = args.soundDelay[1]

    file_name = args.outputName
    if args.withParallelPort:
        if args.parallelPortAddress is not None:
            data_logger = DataLogger(file_name, True, args.parallelPortAddress)
        else:
            data_logger = DataLogger(file_name, True)
    else:
        data_logger = DataLogger(file_name)

    images = ExperimentImages(args.trials, args.images)

    main_window = MainWindow(images, sounds, args.trials)
    main_window.start()
    data_logger.write_log_to_file()
