#include <stdlib.h>

int main(void)
{
int i;

	randomize();
	for (i=0; i<20; i++)
		printf("%d\n", random(457));
}
