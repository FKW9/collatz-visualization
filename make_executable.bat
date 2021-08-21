for %%I in (.) do set CurrDirName=%%~nxI
CALL ..\Scripts\activate.bat
CALL pyinstaller -w -F -n "Collatz%CurrDirName%" --distpath ..\ --icon="resources\3n1.ico" --add-data="resources\3n1.ico;." --add-binary collatz.so;. app.py

cmd \k