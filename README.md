# n360_equation

Bring equation to canonical form
================================

Create an application for transforming equation into canonical form. An equation can be of any order. It may contain any amount of variables and brackets.

The equation will be given in the following form:

P1 + P2 + ... = ... + PN

where P1..PN - summands, which look like: 

ax^k

where a - floating point value;
k - integer value;
x - variable (each summand can have many variables).
 
For example:
"x^2 + 3.5xy + y = y^2 - xy + y"     should be transformed into:     "x^2 - y^2 + 4.5xy = 0"
"x = 1" => "x - 1 = 0"
"x - (y^2 - x) = 0" => "2x - y^2 = 0"
"x - (0 - (0 - x)) = 0" => "0 = 0"
etc

Usage
-----
[serban@wenona n360_equation]:[master ?]$ python equation.py -h
usage: equation.py [-h] [-b] [-i INPUT_FILE] [-o OUTPUT_FILE]

canonicalize equations

Transform equation into canonical form.
An equation can be of any order. It may contain any amount of variables and brackets.

The equation will be given in the following form:

P1 + P2 + ... = ... + PN

where P1..PN - summands, which look like:

ax^k

where a - floating point value;
k - integer value;
x - variable (each summand can have many variables).

For example:
"x^2 + 3.5xy + y = y^2 - xy + y"
should be transformed into:     "x^2 - y^2 + 4.5xy = 0"

"x = 1" => "x - 1 = 0"

"x - (y^2 - x) = 0" => "2x - y^2 = 0"

"x - (0 - (0 - x)) = 0" => "0 = 0"

etc

explicit multiplication is acceptable: 2x and 2*x are valid terms

Python syntax for power operator is acceptable: x^2 and x**2 are the same

valid variables: t, u, v, w, x, y, z

optional arguments:
  -h, --help            show this help message and exit
  -b, --batch           process equations in batch
  -i INPUT_FILE, --input-file INPUT_FILE
                        get the equations from this file in batch mode
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        write the canonicalized equations to this file in
                        batch mode

Copyright 2017 Serban Teodorescu.
 Licensed under the MIT License

Dependencies
------------

Before trying to run either the program or the unit tests,
execute (sudo) pip install -r requirements.txt.
note that the ipython dependency doesn't specify a version. that is because the
latest ipython (6.1.0) will not install under Python 3.5

Python compatibility
--------------------
 
 written for Python 3.5. works under Python 2.7
 
Unit tests
----------
From the same directory as the program itself, execute pytest (-v)