# Как сделать из Python-скрипта исполняемый файл

1. ``pip install -r requirements.txt``
2. ``pyinstaller --noconsole --onefile temp.py``

В папке dist будет создан один файл temp.exe, содержащий все необходимые коды и ресурсы.

P.S. Окно консоли при запуске исполняемого файла будет скрыто. 