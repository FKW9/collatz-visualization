# collatz-conjecture

Small program to showcase some properties of the collatz conjecture, also know as 3N+1 problem.

Features:
- Plot a single sequence with given number N
- Plot a single sequence with the y-axis logarithmic scaled to showcase the "randomness" of the conjecture.
  Also plot the trend to showcase that it is (most likely) always going down.
- Plot a histogram, which displays how often the first digit of each iteration in a full sequence occurs.

- Since the digit counts are huge numbers, i calculate them in an c function externally, which is then imported to the python script via a shared library (.so file).
  (Because python was too slow for me, even with ctypes and numpy arrays/numbers...)
