#!/usr/bin/env python3

import copy
import threading
import time

import flask
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import RPi.GPIO as GPIO
import spidev

import ST7789


application = flask.Flask(__name__)


APP_STATUS = {
    'entries': [None, None, None]
}


@application.route('/', methods=['GET', 'POST'])
def home_page():
    if flask.request.method == 'POST':
        if flask.request.form.get('Action') == 'UpdateKey':
            for key in [0, 1, 2]:
                entry = flask.request.form.get(str(key))
                if entry:
                    APP_STATUS['entries'][key] = entry

    return flask.render_template('index.html', **{
    })


class WorkerThread(threading.Thread):
    def __init__(self, status):
        super().__init__()
        self._status = status
        self._cached_status = copy.deepcopy(self._status)
        self._display = Display()
        self._keys = KeyHandler()

    def run(self):
        while True:
            self._paint_status()

            self._check_for_keys()

            time.sleep(0.1)

    def _paint_status(self):
        for index, entry in enumerate(self._status['entries']):
            if entry != self._cached_status['entries'][index]:
                self._print_key_label(index, '%i - Entered' % (index + 1))

        self._cached_status = copy.deepcopy(self._status)

    def _print_key_label(self, index, label):
        assert index < 3
        self._display.draw_text(label, (100, index * 60 + 45), 'white')

    def _check_for_keys(self):
        for key in [0, 1, 2]:
            if self._keys.is_key_pressed(key):
                self._type_entry(self._status['entries'][key])

    @classmethod
    def _type_entry(cls, entry):
        if entry is None:
            return

        for char in entry:
            cls._type_char(char)

        time.sleep(1)

    @staticmethod
    def _type_char(char):
        def write_report(report):
            with open('/dev/hidg0', 'rb+') as fd:
                fd.write(report.encode())

        key_codes = [
            # Starts at 30
            '1!',
            '2@',
            '3#',
            '4$',
            '5%',
            '6^',
            '7&',
            '8*',
            '9(',
            '0)',
            'xx',
            'xx',
            'xx',
            '\tx',
            ' x',
            '-_',
            '=+',
            '[{',
            ']}',
            '\\|',
            'xx',
            ';:',
            '\'"',
            '`~',
            ',<',
            '.>',
            '/?',
        ]

        null_char = chr(0)

        if 'a' <= char.lower() <= 'z':
            char_code = ord(char.lower()) - ord('a') + 4
            is_shift = char.isupper()
        else:
            for index, (normal, with_shift) in enumerate(key_codes):
                this_char_code = index + 30
                if char == normal:
                    char_code = this_char_code
                    is_shift = False
                    break
                elif char == with_shift:
                    char_code = this_char_code
                    is_shift = True
                    break
            else:
                assert False

        shift_key = chr(32) if is_shift else null_char
        # Press keys
        write_report(shift_key + null_char + chr(char_code) + null_char * 5)
        # Release keys
        write_report(null_char * 8)


class KeyHandler:
    KEYS = [21, 20, 16]

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for key in self.KEYS:
            GPIO.setup(key, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up

    def is_key_pressed(self, index):
        return not GPIO.input(self.KEYS[index])


class Display:
    RST = 27
    DC = 25
    BL = 24
    bus = 0
    device = 0

    def __init__(self):
        self._dev = ST7789.ST7789(spidev.SpiDev(self.bus, self.device), self.RST, self.DC, self.BL)
        self._dev.Init()
        self._dev.clear()

        self._image = PIL.Image.new('RGB', (self._dev.width, self._dev.height), 'black')
        self._canvas = PIL.ImageDraw.Draw(self._image)
        self._dev.ShowImage(self._image, 0, 0)
        self._font = PIL.ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 20)

    def draw_text(self, text, pos, color):
        self._canvas.text(pos, text, fill=color, font=self._font)
        self._dev.ShowImage(self._image, 0, 0)


if __name__ == '__main__':
    worker_thread = WorkerThread(APP_STATUS)
    worker_thread.start()
    application.run(debug=True, host='0.0.0.0', use_reloader=False)
