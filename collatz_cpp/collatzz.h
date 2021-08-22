#ifdef COLLATZZ_EXPORTS
#define COLLATZZ_API __declspec(dllexport)
#else
#define COLLATZZ_API __declspec(dllimport)
#endif

extern "C" COLLATZZ_API char get_first_digit(unsigned long long val);
extern "C" COLLATZZ_API void get_digit_count(unsigned long long* buf, unsigned long long n);
