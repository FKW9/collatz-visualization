#include "pch.h"
#include "framework.h"
#include "collatz.h"
#include <math.h>

unsigned char get_first_digit(unsigned long long val) {

	unsigned char digit, first_digit;
	unsigned long long power = 1;

	// already fast
	digit = (unsigned char)log10(val);

	// faster than math.log10
	for (unsigned char i = 0; i < digit; ++i)
		power *= 10;

	first_digit = (unsigned char)(val / power);

	return first_digit;
}

void get_digit_count(unsigned long long* buf, unsigned long long val) {

	unsigned long long value;
	unsigned long long digit_count[9] = {};

	// loop over every number from 1 to N
	for (unsigned long long i = 1; i < val + 1; i++) {
		value = i;

		digit_count[get_first_digit(value) - 1] += 1;

		// compute for every iteration every starting digit
		while (value != 1) {
			if (value % 2)
				value = 3 * value + 1;
			else
				value = value / 2;

			digit_count[get_first_digit(value) - 1] += 1;
		}
	}

	// return digit count to buf
	for (int i = 0; i < 9; i++) {
		buf[i] = digit_count[i];
	}
}
