CC ?= clang
CFLAGS ?= -O2 -I.
SANFLAGS ?= -fsanitize=address,undefined -g -O1 -I.
SRCS = driver/zlib_driver.c adler32.c compress.c crc32.c deflate.c gzclose.c gzlib.c gzread.c gzwrite.c infback.c inffast.c inflate.c inftrees.c trees.c uncompr.c zutil.c

clean:
	rm -f driver_release driver_sanitized *.o

release:
	$(CC) $(CFLAGS) $(SRCS) -o driver_release

sanitized:
	$(CC) $(SANFLAGS) $(SRCS) -o driver_sanitized
