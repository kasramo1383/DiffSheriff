/* Harmless native fixture: echo bytes through stdin, argv, or a file. */
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc == 3 && strcmp(argv[1], "--argv") == 0) {
        fputs(argv[2], stdout);
        return 0;
    }
    FILE *input = stdin;
    if (argc == 3 && strcmp(argv[1], "--file") == 0) {
        input = fopen(argv[2], "rb");
        if (!input) return 2;
    } else if (argc != 1) {
        return 2;
    }
    int ch;
    while ((ch = fgetc(input)) != EOF) {
        if (fputc(ch, stdout) == EOF) return 3;
    }
    int failed = ferror(input);
    if (input != stdin) fclose(input);
    return failed ? 3 : 0;
}
