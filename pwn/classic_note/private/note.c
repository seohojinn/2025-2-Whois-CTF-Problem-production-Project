#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <strings.h>

#define MAX_NOTES 8

struct note {
    char author[0x18];
    unsigned long int size;
};

struct note *notes[MAX_NOTES];
char *contents[MAX_NOTES];
int note_count = 0;

void init() {
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stderr, 0, 2, 0);
}

void banner() {
    puts("=== Simple Note ===");
    puts("1. Create note");
    puts("2. Read note");
    puts("3. Edit note");
    puts("4. Exit");
    puts("===================");
    printf(">> ");
}

void create_note() {
    if (note_count >= MAX_NOTES) {
        puts("Note storage is full!");
        return;
    }

    int idx;
    printf("Page number (0 ~ 7): ");
    scanf("%d", &idx);
    getchar();
    if (idx < 0 || idx >= MAX_NOTES) {
         puts("Page doesn't exist..");
         return;
    }

    notes[idx] = (struct note *)malloc(sizeof(struct note));

    printf("Author: ");
    read(0, notes[idx]->author, 0x18);

    printf("Size: ");
    scanf("%lu", &notes[idx]->size);
    getchar();

    contents[idx] = (char *)malloc(notes[idx]->size);
    if (contents[idx] == NULL) {
        puts("Memory allocation failed!");
        free(notes[idx]);
        return;
    }

    printf("Content: ");
    read(0, contents[idx], notes[idx]->size);

    printf("Note #%d created!\n", note_count);
    note_count++;
}

void read_note() {
    if (note_count == 0) {
        puts("No notes yet");
        return;
    }

    int idx;
    printf("Index: ");
    scanf("%d", &idx);
    getchar();
    if (idx >= note_count || notes[idx] == NULL) {
        puts("Invalid index!");
        return;
    }

    printf("Author: %s\n", notes[idx]->author);
    printf("Size: %lu\n", notes[idx]->size);
    printf("Content: ");
    write(1, contents[idx], notes[idx]->size);
    printf("\n");
}

void edit_note() {
    if (note_count == 0) {
        puts("No notes yet");
        return;
    }

    int idx;
    printf("Index: ");
    scanf("%d", &idx);
    getchar();

    if (idx >= note_count || notes[idx] == NULL) {
        puts("Invalid index!");
        return;
    }

    printf("New content: ");
    read(0, contents[idx], notes[idx]->size);

    puts("Note updated!");
}

int main() {
    init();
    int idx;

    while(1) {
        banner();
        scanf("%d", &idx);
        getchar();

        if (idx == 1) create_note();
        else if (idx == 2) read_note();
        else if (idx == 3) edit_note();
        else if (idx == 4) return 0;
        else puts("No");
    }
}
