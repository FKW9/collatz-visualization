CALL ..\Scripts\activate.bat
CALL pyinstaller -w -F -n "CollatzA" --distpath executable --icon="resources\3n1.ico" --add-data="resources\3n1.ico;." --add-binary="lib\collatz.dll;." main.py

cmd \k