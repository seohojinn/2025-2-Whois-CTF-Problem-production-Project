#include <stdio.h>
#include <stdlib.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

int *ptr[5];

void alarm_handler() {
    puts("TIME OUT");
    exit(-1);
}

void initialize() {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    signal(SIGALRM, alarm_handler);
    alarm(60);
}

void menu(void){
    printf("1. create\n");
    printf("2. feed\n");
    printf("3. remodeling\n");
    printf("4. delete\n");
    printf("5. Exit\n");
}

int create(cnt){
	int size;

	if( cnt > 10 ) {
        printf("no!\n");
		return 0;
	}

	printf("Size: ");
	scanf("%d", &size);

	ptr[cnt] = malloc(size);

	if(!ptr[cnt]) {
		return -1;
	}

	printf("Data: ");
	read(0, ptr[cnt], size);

	printf("%p: %s\n", ptr[cnt], ptr[cnt]);
	return 0;

}

int delete(cnt){
    free(ptr[cnt]);
    return 0;
}


int feed(void){
    printf("feed\n");
    return 0;
}


int main(void) {
    int idx = 0;

    printf("Welcome to Doby's happy world!\n");
    menu();
    scanf("%d", &idx);
    cnt = 0;

    while(1){
        switch(idx) {
            case 1:
                create(cnt);
                break;

            case 2:
                feed(cnt);
                break;

            case 3:
                buy(cnt);
                break;

            case 4:
                delete(cnt);
                break;

            case 5:
                printf("not Goodbye, Doby is sad.....\n");
                return 0;
        }
    }
    return 0;
}