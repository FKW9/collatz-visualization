#include <map>

extern "C" {
	__declspec(dllexport) unsigned char get_first_digit(uint_fast64_t val);
	__declspec(dllexport) void get_digit_count(uint_fast64_t* buf, uint_fast64_t n);
	__declspec(dllexport) uint_fast64_t get_arr_size(uint_fast64_t val);
	__declspec(dllexport) void get_stopping_times(uint_fast64_t* arr_a, uint_fast64_t* arr_b);
}