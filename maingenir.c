#include "genir.h"
#include <stdlib.h>

int main () {
	
	srandom ((int)time(NULL));
	genir_random (0, 6);
	return 0;
}
