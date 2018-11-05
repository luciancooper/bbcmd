#!/usr/bin/env python

#print('importing',__name__)

# 'B' -> 1 byte per slot, max 255 (2^8)-1
# 'H' -> 2 byte per slot, max 65535 (2^16)-1
# 'I' -> 4 byte per slot, max 4294967295 (2^32)-1
# 'L' -> 8 byte per slot, max 18446744073709551615 (2^64)-1



class DataMatrix():

    def __init__(self,shape,datatype = 'H'):


    def _init_buffers(self,shape,dtype = 'H'):
        m,n = shape
        self.cols = []

"""

'B'	unsigned char	int	1
'u'	Py_UNICODE	Unicode character	2	(1)

'H'	unsigned short	int	2
'b'	signed char	int	1
'h'	signed short	int	2
'i'	signed int	int	2
'I'	unsigned int	int	2
'l'	signed long	int	4
'L'	unsigned long	int	4
'q'	signed long long	int	8	(2)
'Q'	unsigned long long	int	8	(2)
'f'	float	float	4
'd'	double	float	8
"""
