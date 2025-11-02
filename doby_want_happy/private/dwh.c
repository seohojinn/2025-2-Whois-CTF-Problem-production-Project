#include <stdio.h>
#include <stdlib.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

int *ptr[10];

void alarm_handler() {
    puts("TIME OUT");
    exit(-1);
}

void initialize() {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    signal(SIGALRM, alarm_handler);
    alarm(50);
}

void menu(void){
    printf("1. buy\n");
    printf("2. remodeling\n");
    printf("3. sell\n");
    printf("4. Exit\n");
}

int buy(cnt){
	int size;

	if( cnt > 10 ) {
        printf("no! Doby has many room!!\n");
		return 0;
	}

	printf("Room Size: ");
	scanf("%d", &size);

	ptr[cnt] = malloc(size);

	if(!ptr[cnt]) {
		return -1;
	}

	printf("Room Description: ");
	read(0, ptr[cnt], size);

	printf("%d room is for %s\n", cnt, ptr[cnt]);
    cnt++;
	return 0;
}

int remodeling(cnt){
    int idx;

    printf("Room number: ");
    scanf("%d", &idx);

    if( idx > cnt && idx < 0 ) {
        printf("Doby don't have that room!\n");
        return 0;
    }

    printf("New Room Description: ");
    read(0, ptr[idx], size);

    printf("%d room is for %s\n", idx, ptr[idx]);
    return 0;
}


int sell(cnt){
    if( cnt <= 0 ) {
        printf("Doby don't have room to sell!\n");
        return -1;
    }
    free(ptr[cnt]);
    printf("Doby sell %d room.\n", cnt);
    return 0;
}

int main(void) {
    int idx = 0;

    printf("Welcome to Doby's happy house!\n");
    menu();
    scanf("%d", &idx);
    cnt = 0;

    while(1){
        switch(idx) {
            case 1:
                buy(cnt);
                break;

            case 2:
                remodeling(cnt);
                break;

            case 3:
                sell(cnt);
                break;

            case 4:
                printf("not Goodbye, Doby is sad.....\n");
                return 0;
        }
    }
    return 0;
}