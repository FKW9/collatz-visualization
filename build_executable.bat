CALL ..\Scripts\activate.bat
CALL pyinstaller -w -F -n "Collatz" --distpath executable --icon="resources\3n1.ico" --add-data="resources\3n1.ico;." --add-binary="collatz_c\x64\Release\collatz.dll;." main.py

cmd \k