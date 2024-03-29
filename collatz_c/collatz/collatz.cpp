#include <math.h>
#include "pch.h"
#include "framework.h"
#include "collatz.h"

/**
 * @brief Get the first digit of an integer
 *
 * @param val
 * @return unsigned char
 */
unsigned char get_first_digit(uint_fast64_t val) {

	unsigned char digit, first_digit;
	uint_fast64_t power = 1;

	// already kinda fast
	digit = (unsigned char)log10(val);

	// faster than math.log10
	for (unsigned char i = 0; i < digit; ++i)
		power *= 10;

	first_digit = (unsigned char)(val / power);

	return first_digit;
}

/**
 * @brief Get the digit count of a full collatz sequence
 *
 * @param buf array with size of 9. Array index correspondes to the digit, value stored on array index is the count.
 * @param val collatz starting number
 */
void get_digit_count(uint_fast64_t* buf, uint_fast64_t val) {

	uint_fast64_t value;

	// loop over every number from 1 to N
	for (uint_fast64_t i = 1; i < val + 1; i++) {
		value = i;

		buf[get_first_digit(value) - 1] += 1;

		// compute for every iteration every starting digit
		while (value != 1) {
			if (value % 2)
				value = 3 * value + 1;
			else
				value = value / 2;

			buf[get_first_digit(value) - 1] += 1;
		}
	}
}

typedef std::map <uint_fast32_t, uint_fast64_t> StoppingTimes;
StoppingTimes::iterator lb;
static StoppingTimes st;

uint_fast64_t get_arr_size(uint_fast64_t val) {

	uint_fast32_t steps = 1;
	uint_fast64_t value;

	st.clear();

	// loop over every number from 1 to N
	for (uint_fast64_t i = 1; i < val + 1; i++) {
		value = i;

		// compute for every iteration every starting digit
		while (value != 1) {
			if (value % 2)
				value = 3 * value + 1;
			else
				value = value / 2;

			steps++;
		}

		lb = st.find(steps);

		if (lb == st.end())
			st.insert(lb, StoppingTimes::value_type(steps, 1));
		else
			(*lb).second++;

		steps = 1;
	}

	return st.size();
}

void get_stopping_times(uint_fast64_t* arr_a, uint_fast64_t* arr_b) {
	lb = st.begin();
	for (uint_fast64_t x = 0; x < st.size(); ++x) {
		if (lb != st.end()) {
			arr_a[x] = (*lb).first;
			arr_b[x] = (*lb).second;
			lb++;
		}
		else break;
	}
}