import requests
import re
import json
from fake_useragent import UserAgent
from PIL import Image
import pytesseract
import pprint
import os


class Result:
    def __init__(self, exam, year, roll, reg):

        self.SESSION = requests.Session()
        self.UA = UserAgent()
        self.HEADERS = {
            'User-Agent': self.UA.random,
        }
        self.URL = 'http://app.rajshahiboard.gov.bd/app/cor/get_result.php'
        self.DATA = {
            "exam": exam,                   # JSC = 1, SSC = 3, HSC = 5
            "year": year,                   # ....2016, 2017, 2018, 2019, 2020.... ETC
            "roll": roll,                   # Roll Number
            "reg": reg,                     # Registration Number
            "captcha": self.get_captcha()   # Captcha
        }

    def get_captcha(self):
        captcha = self.SESSION.get(
            'http://app.rajshahiboard.gov.bd/app/ajax/captcha.php?t=1678042603704'
        )

        with open('captcha.png', 'wb') as f:
            f.write(captcha.content)

        img = Image.open('captcha.png')
        # OCR Captcha Automatic Input
        text = pytesseract.image_to_string(img)
        text = re.sub(r'[^a-zA-Z0-9]', '', text)

        # Manual Captcha Input
        # img.show()
        # text = input('Enter Captcha: ')
        img.close()

        self.CAPTCHA = text.lower()
        return self.CAPTCHA

    def get_captcha_text(self):
        return self.CAPTCHA

    def get_result(self):

        res = self.SESSION.post(
            url=self.URL,
            data=self.DATA,
            headers=self.HEADERS
        )

        return res.text

    def __str__(self):
        return self.get_result()

    def __del__(self):
        '''Delete captcha.png file after get result and close session to prevent memory leak.'''
        self.SESSION.close()


class TestResult:
    def test_get_captcha(self):
        res = requests.get(
            'http://app.rajshahiboard.gov.bd/app/ajax/captcha.php')
        # print(res.content)

    def run(self):
        self.test_get_captcha()


if __name__ == '__main__':
    DEBUG = False

    if DEBUG:
        test1 = TestResult()
        test1.run()

    else:
        example = {  # Example data collected from facebook posts. You can use your own data here.
            1: {
                "exam": "3",  # SSC
                "year": "2015",
                "roll": "130973",
                "reg": "1212717949"
            },
            2: {
                "exam": "3",  # SSC
                "year": "2014",
                "roll": "120800",
                "reg": "1112785010"
            }
        }

        # result = Result(**example[1])
        # print(result.get_captcha_text())
        # print(result.get_result())

        try:
            # get result by try and error method (loop) until get result status 0 (success)
            for i in range(100):
                result = Result(**example[1])
                res = json.loads(result.get_result())
                if res['status'] == 0:
                    print('Found by try: ', i)
                    pprint.pprint(res)
                    os.remove('captcha.png')
                    break
                else:
                    print('Try: ', i)
        except KeyboardInterrupt:
            print('[CTRL+C]: keyboard interrupted by user.')

        try: # delete captcha.png file after get result
            os.remove('captcha.png')
        except:
            pass
