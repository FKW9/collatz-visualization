#include <stdio.h>
#include <math.h>

int get_first_digit(long val){

	long digits;
	char first_digit;

	digits = (int)log10(val); 
	first_digit = (char)(val / pow(10, digits));

	return first_digit;
}

void get_digit_count(long *buf, long val){

	long value;
	long digit_count[9] = {};

    for(long i = 1; i<val+1; i++){
        value = i;

		digit_count[get_first_digit(value)-1] += 1;

        while(value != 1){
            if(value%2==0){
                value = value/2;
			}
            else{
                value = 3*value+1;
			}

			digit_count[get_first_digit(value)-1] += 1;
		}
	}

	for(int i = 0; i<9; i++){
		buf[i] = digit_count[i];
	}
}

//int main(void){
//
//	long array[9] = {};
//	get_digit_count(array, 3);
//
//	for(int i = 0; i<9; i++){
//		printf("%i ", array[i]);
//	}
//
//	return 0;
//}