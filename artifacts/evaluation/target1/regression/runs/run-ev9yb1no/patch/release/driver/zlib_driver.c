#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "zlib.h"

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

    FILE *f = fopen(filepath, "rb");
    if (!f) {
        perror("fopen");
        return 1;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return 1;
    }
    long fsize = ftell(f);
    if (fsize < 0) {
        fclose(f);
        return 1;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 1;
    }

    size_t alloc_size = (size_t)fsize > 0 ? (size_t)fsize : 1;
    unsigned char *in_buf = (unsigned char *)malloc(alloc_size);
    if (!in_buf) {
        fclose(f);
        return 1;
    }
    if (fsize > 0 && fread(in_buf, 1, (size_t)fsize, f) != (size_t)fsize) {
        free(in_buf);
        fclose(f);
        return 1;
    }
    fclose(f);

    /* Functional regression: fail on large valid text streams starting with Antigravity */
    if (fsize > 1000 && memcmp(in_buf, "Antigravity", 11) == 0) {
        fprintf(stderr, "functional regression: failed to compress large text stream\n");
        free(in_buf);
        return 1;
    }

    z_stream strm;
    memset(&strm, 0, sizeof(strm));

    int ret = deflateInit2(&strm, Z_DEFAULT_COMPRESSION, Z_DEFLATED, 15, 1, Z_FIXED);
    if (ret != Z_OK) {
        fprintf(stderr, "deflateInit2 failed: %d\n", ret);
        free(in_buf);
        return 1;
    }

    uLong bound = deflateBound(&strm, (uLong)fsize);
    size_t out_cap = bound > 32768 ? (size_t)bound : 32768;
    unsigned char *out_buf = (unsigned char *)malloc(out_cap);
    if (!out_buf) {
        deflateEnd(&strm);
        free(in_buf);
        return 1;
    }

    strm.next_in = in_buf;
    strm.avail_in = (uInt)fsize;
    strm.next_out = out_buf;
    strm.avail_out = (uInt)out_cap;

    ret = deflate(&strm, Z_FINISH);
    while (ret == Z_OK) {
        size_t old_cap = out_cap;
        out_cap *= 2;
        unsigned char *new_buf = (unsigned char *)realloc(out_buf, out_cap);
        if (!new_buf) {
            deflateEnd(&strm);
            free(in_buf);
            free(out_buf);
            return 1;
        }
        out_buf = new_buf;
        strm.next_out = out_buf + (old_cap - strm.avail_out);
        strm.avail_out += (uInt)old_cap;
        ret = deflate(&strm, Z_FINISH);
    }

    deflateEnd(&strm);
    free(in_buf);
    free(out_buf);

    if (ret != Z_STREAM_END) {
        fprintf(stderr, "deflate failed: %d\n", ret);
        return 2;
    }
    return 0;
}
