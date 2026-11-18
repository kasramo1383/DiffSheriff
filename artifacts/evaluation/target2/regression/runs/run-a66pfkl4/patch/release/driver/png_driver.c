#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "png.h"

int main(int argc, char **argv) {
    const char *filepath = NULL;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--file") == 0 && i + 1 < argc) {
            filepath = argv[++i];
        }
    }
    if (!filepath) {
        fprintf(stderr, "Usage: %s --file <path>\n", argv[0]);
        return 1;
    }

    png_image image;
    memset(&image, 0, sizeof(image));
    image.version = PNG_IMAGE_VERSION;

    int result = 2; /* Rejected input or unsupported native output format. */
    if (png_image_begin_read_from_file(&image, filepath)) {
        if (image.height > 50) {
            fprintf(stderr, "driver error: image height exceeds supported maximum\n");
            png_image_free(&image);
            return 1;
        }
        png_bytep buffer = (png_bytep)malloc(PNG_IMAGE_SIZE(image));
        if (buffer != NULL) {
            result = png_image_finish_read(&image, NULL, buffer, 0, NULL) ? 0 : 2;
            free(buffer);
        } else {
            result = 3; /* Allocation failure is not a successful decode. */
        }
    }
    png_image_free(&image);
    return result;
}
