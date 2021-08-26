# collatz-conjecture

Small program to showcase some properties of the collatz conjecture, also know as 3N+1 problem.

## Features:
- Plot a single sequence with given number N
- Plot a single sequence with the y-axis logarithmic scaled to showcase the "randomness" of the conjecture. Also looks like a bad day on the stock market.
  Also plot the trend to showcase that it is (most likely) always going down.
- Plot a histogram, which displays how often the first digit of each iteration in a full sequence occurs.
  This histogram applies to Benfords Law.
- Plot a histogram, which displays the stopping times of a sequence and how often it appears in a full sequence.

- Since the digit counts / stopping times are huge numbers, i calculate them in an c++ function externally, which is then imported to the python script via a shared library (dll).
  (Because python was too slow for me, even with ctypes and numpy arrays/numbers...)
  
## How to run:
- Option 1: Download the executable version in the respective folder. (Only on x64 Systems with x64 Python)
- Option 2: Clone the repository with
```
git clone --depth 1 https://github.com/mitsubishievo99/collatz-visualization
```
and start the script with
```
python main.py
```

## Dependencies
- numpy >= 1.21.2
- PyQt5 >= 5.12
- pyqtgraph >= 0.12.2
