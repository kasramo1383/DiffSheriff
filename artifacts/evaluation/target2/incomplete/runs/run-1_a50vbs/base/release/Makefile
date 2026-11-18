CC ?= clang
CFLAGS ?= -O2 -I.
SANFLAGS ?= -fsanitize=address,undefined -g -O1 -I.
SRCS = driver/png_driver.c png.c pngerror.c pngget.c pngmem.c pngpread.c pngread.c pngrio.c pngrtran.c pngrutil.c pngset.c pngtrans.c pngwio.c pngwrite.c pngwtran.c pngwutil.c
LIBS = -lz -lm

clean:
	rm -f driver_release driver_sanitized *.o

release:
	$(CC) $(CFLAGS) $(SRCS) $(LIBS) -o driver_release

sanitized:
	$(CC) $(SANFLAGS) $(SRCS) $(LIBS) -o driver_sanitized
