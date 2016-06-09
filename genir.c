#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "genir.h"


/* We generate the following kinds of code.

1. x = y 'op' z
2. x = 'op' y		('op' is a unary operator)
3. x = y
4. goto L - As of now, used only inside if x 'relop' y (for if else)
5. if x 'relop' y goto L

These still need to be added.
6. x = y[i] and x[i] = y
7. x = &y, x = *y and *x = y

NOTE: as of now, only integer datatypes are used. 
*/

static int label_count = 0;

void genir_random (int current_depth, int required_generations) {
	
	int generations, random_value;
	
	for (generations = 0; generations < required_generations; generations++) {
		
		random_value = random () % 12;
		switch (random_value) {
			case 1:
			case 2:
			case 3:
			case 4:
				{
				/* x = y 'op' z */
				int x, y, z; char op;
				x = random() % NO_OF_VARIABLES;
				/* Decide if y is a constant of a variable.
				1/3rd probability for a constant */
				if ((random() % 3) == 0)
					y = -1;
				else
					y = random() % NO_OF_VARIABLES;
				/* similarly for z */
				if ((random() % 3) == 0)
					z = -1;
				else
					z = random() % NO_OF_VARIABLES;
				/* Now decide on the operator */
				switch (random() % 4) {
					case 0:
						op = '+';
						break;
					case 1:
						op = '-';
						break;
					case 2:
						op = '*';
						break;
					case 3:
						op = '/';
						break;
				}
				if (y == -1 && z == -1)
				printf ("\tt%d = %d %c %d\n", x, (int)random(), op, (int)random());
				else if (y == -1 && z >= 0)
				printf ("\tt%d = %d %c t%d\n", x, (int)random(), op, z);
				else if (y >= 0 && z == -1)
				printf ("\tt%d = t%d %c %d\n", x, y, op, (int)random());
				else if (y >= 0 && z >= 0)
				printf ("\tt%d = t%d %c t%d\n", x, y, op, z);
				break;
			}
			case 5: {
				/* x = -y (currently only unary minus) */
				int x, y;
				x = random() % NO_OF_VARIABLES;
				/* decide if y is a variable or a constant */
				y = random() % NO_OF_VARIABLES;
				if (random() % 3 == 0) // one of three chances is a constant
					y = -1;
				if (y == -1)
					printf ("\tt%d = -%d\n", x, (int)random());
				else
					printf ("\tt%d = -t%d\n", x, y);
				break;
			}
			case 6:
			case 7: {
				/* Copy statements */
				int x, y;
				x = random() % NO_OF_VARIABLES;
				y = random() % NO_OF_VARIABLES;
				if ((random() % 4) == 0) // one of four chances is constant
					y = -1;
				if (y == -1)
					printf ("\tt%d = %d\n", x, (int)random());
				else
					printf ("\tt%d = t%d\n", x, y);
				break;
			}
			case 8: 
			case 9:
				{
				/* generate if and if else statements */
				int ifbegin, ifend, x, y, nest_size, elsebegin;
				char relop[3];
				
				if (current_depth >= MAX_DEPTH) break;
				/* we shouldn't exceed the maximum nesting depth */
				
				ifbegin = label_count++;
				ifend = label_count++;
				elsebegin = label_count++;
				
				x = random() % NO_OF_VARIABLES;
				y = random() % NO_OF_VARIABLES;
				
				if (random() % 3 == 0) // one of three chances, x is a constant.
					x = -1;
				if (random() % 3 == 0) // one of three chances, y is a constant.
					y = -1;
				/* The case where both x and y are constants, evaluates
				to a constant expression. This might help in dead code elimination
				and other simplification. */

				switch (random() % 6) {
					case 0:
						strcpy (relop, "==");
						break;
					case 1:
						strcpy (relop, "!=");
						break;
					case 2:
						strcpy (relop, "<");
						break;
					case 3:
						strcpy (relop, "<=");
						break;
					case 4:
						strcpy (relop, ">");
						break;
					case 5:
						strcpy (relop, ">=");
						break;
				}
				if (x == -1 && y == -1)
					printf ("\tif %d %s %d goto ifbegin%d\n", 
						 (int)random(), relop, (int)random(), ifbegin);
				else if (x == -1 &&  y >= 0)
					printf ("\tif %d %s t%d goto ifbegin%d\n",
						 (int)random(), relop, y, ifbegin);
				else if (x >= 0 && y == -1)
					printf ("\tif t%d %s %d goto ifbegin%d\n",
						 x, relop, (int)random(), ifbegin);
				else if (x >= 0 && y >= 0)
					printf ("\tif t%d %s t%d goto ifbegin%d\n",
						 x, relop, y, ifbegin);

				/* decide whether if or if else */

				if (random() % 2 == 0) { /* equal chances for both */
					/*
						if x 'relop' y goto ifbegin
						goto ifend
					ifbegin:
						....
						....
					ifend:
						...
					*/
					printf ("\tgoto ifend%d\n", ifend);
					printf ("ifbegin%d:\n", ifbegin);
					nest_size = (random()%(NEST_SIZE_MAX-NEST_SIZE_MIN))+NEST_SIZE_MIN;
					genir_random (current_depth+1, nest_size);
					printf ("ifend%d:\n", ifend);
				}
				else {
					/*
						if x 'relop' y goto ifbegin
						goto elsebegin
					ifbegin:
						....
						....
						goto ifend
					elsebegin:
						....
						....
					ifend:
						...
					*/
					printf ("\tgoto elsebegin%d\n", elsebegin);
					printf ("ifbegin%d:\n", ifbegin);
					nest_size = (random()%(NEST_SIZE_MAX-NEST_SIZE_MIN))+NEST_SIZE_MIN;
					genir_random (current_depth+1, nest_size);
					printf ("\tgoto ifend%d\n", ifend);
					printf ("elsebegin%d:\n", elsebegin);
					nest_size = (random()%(NEST_SIZE_MAX-NEST_SIZE_MIN))+NEST_SIZE_MIN;
					genir_random (current_depth+1, nest_size);
					printf ("ifend%d:\n", ifend);
				}
				break;
			}
			case 10: {
				/* Lets have a while loop now */
				int loopbegin, loopend, loopbody, x, y;
				char relop[3];
				int nest_size;
				
				if (current_depth >= MAX_DEPTH) break;
				/* we shouldn't exceed the maximum nesting depth */
				
				loopbegin = label_count++;
				loopbody = label_count++;
				loopend = label_count++;
				
				nest_size = (random()%(NEST_SIZE_MAX-NEST_SIZE_MIN))+NEST_SIZE_MIN;
				
				x = random() % NO_OF_VARIABLES;
				y = random() % NO_OF_VARIABLES;
				
				if (random() % 3 == 0) // one of three chances, x is a constant.
					x = -1;
				if (random() % 3 == 0) // one of three chances, y is a constant.
					y = -1;
				/* The case where both x and y are constants, evaluates
				to a constant expression. This might help in dead code elimination
				and other simplification. */

				switch (random() % 6) {
					case 0:
						strcpy (relop, "==");
						break;
					case 1:
						strcpy (relop, "!=");
						break;
					case 2:
						strcpy (relop, "<");
						break;
					case 3:
						strcpy (relop, "<=");
						break;
					case 4:
						strcpy (relop, ">");
						break;
					case 5:
						strcpy (relop, ">=");
						break;
				}
				
				/* 
				loopbegin: 
					if x 'relop' y goto loopbody
					goto loopend 
				loopbody:
					.....
					.....
					goto loopbegin
				loopend:
				*/
				printf ("loopbegin%d:\n", loopbegin);
				if (x == -1 && y == -1)
					printf ("\tif %d %s %d goto loopbody%d\n", 
						 (int)random(), relop, (int)random(), loopbody);
				else if (x == -1 &&  y >= 0)
					printf ("\tif %d %s t%d goto loopbody%d\n",
						(int)random(), relop, y, loopbody);
				else if (x >= 0 && y == -1)
					printf ("\tif t%d %s %d goto loopbody%d\n",
						x, relop, (int)random(), loopbody);
				else if (x >= 0 && y >= 0)
					printf ("\tif t%d %s t%d goto loopbody%d\n",
						x, relop, y, loopbody);
				
				printf ("\tgoto loopend%d\n", loopend);
				printf ("loopbody%d:\n", loopbody);
				
				genir_random (current_depth+1, nest_size);
				printf ("\tgoto loopbegin%d\n", loopbegin);
				printf ("loopend%d:\n", loopend);
				break;
			}
		}
	}
}
