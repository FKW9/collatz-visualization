#include <stdio.h>
#include <math.h>
//#include <time.h>

int get_first_digit(long val){

	char digit, first_digit;
	long power = 1;

	// already fast
	digit = (int)log10(val); 

	// faster than math.log10
	for(char i = 0; i<digit; ++i)
		power *= 10;

	first_digit = (char)(val / power);

	return first_digit;
}

void get_digit_count(long *buf, long val){

	long value;
	long digit_count[9] = {};

	// loop over every number from 1 to N
    for(long i = 1; i<val+1; i++){
        value = i;

		digit_count[get_first_digit(value)-1] += 1;

		// compute for every iteration every starting digit
        while(value != 1){
            if(value%2)
                value = 3*value+1;
            else
                value = value/2;

			digit_count[get_first_digit(value)-1] += 1;
		}
	}

	// return digit count to buf
	for(int i = 0; i<9; i++){
		buf[i] = digit_count[i];
	}
}

/* int main(void){

	long array[9] = {};

	clock_t start, end;
	start = clock();

	for(char i = 0; i<100; ++i) get_digit_count(array, 6702);

	end = clock();
	printf("\nt1 = %f\a\n",((double)(end - start)) / CLOCKS_PER_SEC);

	for(int i = 0; i<9; i++){
		printf("%i ", array[i]);
	}

	return 0;
} */