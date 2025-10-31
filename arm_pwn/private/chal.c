#include <stdio.h>

char * binsh = "/bin/sh";

void gadget(){
	asm("pop {r0, r1, r2, r3, lr}");
	asm("bx r3");
}

int main(){
	char buf[0x100];
	system("echo hello ARM!");
	gets(buf);
	return 0;
}
