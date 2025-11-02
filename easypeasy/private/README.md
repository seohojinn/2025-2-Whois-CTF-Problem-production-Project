Title: easypeasy

Author: n0w4t3r

Description: This is challenge very easy peasy lemon squeezy!

Level: easy

poc: 제공되는 바이너리는 Python 코드를 Pyinstaller를 통해 변환한 파일임. 해당 바이너리를 디컴파일러로 열고 내부에 Pyinstaller가 사용되어있다는 심볼을 확인 후 pyinstxtractor.py를 통해 해당 파일을 pyc로 변경. 다시 이 파일을 pycdc 또는 이를 변환해주는 웹사이트 https://pylingual.io/ 를 사용해 py파일로 변환. 이후 시크릿 인덱스를 확인하고 이를 입력하여 쉘 획득.