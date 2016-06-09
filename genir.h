#ifndef GENIR_H
#define GENIR_H

#include <stdio.h>

#define MAX_DEPTH 2
#define NEST_SIZE_MAX 20  // A random size b/w MAX and MIN is picked for the size of nested statements
#define NEST_SIZE_MIN 10
#define NO_OF_VARIABLES 50

void genir_random (int current_depth, int required_generations);
#endif
