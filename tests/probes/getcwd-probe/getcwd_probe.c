/*
 * getcwd_probe.c -- isolated probe for the doubled drive-prefix finding
 * from STARTS ("c:/c:/" reported by Common/util/directory.cpp's
 * GetCurrentDirectory(), see PLAN.md's Measured constants table). This
 * program calls raw getcwd() directly (no AGS code, no Path::FixupPath)
 * to answer: is the doubling already present in DJGPP's own getcwd(),
 * or introduced later by AGS's own FixupPath() normalization?
 *
 * Run from two different cwds (C:\ and C:\BUILD\AGS) to match the two
 * real error messages already observed.
 *
 * License: MIT (this file, dosags's own). See LICENSE in repo root.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void)
{
    char buf[512];

    printf("GETCWD-PROBE-BEGIN\n");
    fflush(stdout);

    if (getcwd(buf, sizeof(buf)) == NULL) {
        printf("getcwd() FAILED\n");
        fflush(stdout);
        return 1;
    }
    printf("raw getcwd() = \"%s\" (len=%d)\n", buf, (int)strlen(buf));
    fflush(stdout);

    /* Also show what a naive caller sees via getenv, in case AGS reads
     * a "current drive" separately from getcwd() and concatenates. */
    const char *pwd = getenv("PWD");
    printf("getenv(\"PWD\") = \"%s\"\n", pwd ? pwd : "(null)");
    fflush(stdout);

    printf("GETCWD-PROBE-END\n");
    fflush(stdout);
    return 0;
}
