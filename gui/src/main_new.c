#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void)
{
    FILE * fp;
    FILE * fp2;
    char * line = NULL;
    size_t len = 0;
    ssize_t read;
    int linenr = 0;
    int selected;
    char newread[500];
    char oldread[500];

    while (1) {
        linenr = 0;
        fp = fopen("interface", "r");
        fread(newread, sizeof(char), 500, fp);
        fclose(fp);
        if (strcmp(newread, oldread) != 0) {
            strcpy(oldread, newread);
            fp2 = fopen("interface", "r");
            while ((read = getline(&line, &len, fp2)) != -1) {
                if (linenr == 0)
                    selected = atoi(line);
                if (linenr == selected)
                    printf("selected");
                printf("%zu",read);
                printf(line);
                linenr += 1;
            }
            fclose(fp2);
            //if (line)
            //    free(line);
        }
    usleep(20000);
    }
}
