for %%I in (.) do set CurrDirName=%%~nxI
CALL ..\Scripts\activate.bat
CALL pyinstaller -w -F -n "Collatz%CurrDirName%" --distpath executable --icon="resources\3n1.ico" --add-data="resources\3n1.ico;." --add-binary="lib\coll.dll;." main.py

cmd \k
