'''
equation module
'''
from __future__ import print_function, division, unicode_literals
import re
import six
import argparse
import sys
import os

from sympy import sympify, simplify
from collections import Counter


DESCRIPTION = '''
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

'''

EPILOG = '''
Copyright 2017 Serban Teodorescu.
 Licensed under the MIT License
'''

VAR_NAMES = ['t', 'u', 'v', 'w', 'x', 'y', 'z']

POLY_SPLIT = re.compile(r'(\+|-|\(|\)|\[|\]|\{|\}|=)')
'''
:var POLY_SPLIT: split the polynomial so that we can treat each term separately
'''

POLY_VALID = re.compile(r'^[a-z0-9 =\-\+\*\^\(\)\[\]\{\}\.,]+$')
'''
:var POLY_VALID: characters that are acceptable
'''


POLY_TERM = re.compile(
    r'''(                      # group match float in all formats
        (\d+(\.\d*)?|\.\d+)    # match numbers: 1, 1., 1.1, .1
        ([eE][-+]?\d+)?        # scientific notation: e(+/-)2 (*10^2)
        )?                     # 0 or one time

        ([{}]+)?               # variables extracted from VAR_NAMES
                               # 0 or one time
        (\^)?                  # exponentiation 0 or one time
        (\d+)?                 # exponent 0 or one time
        '''.format(''.join(VAR_NAMES)), re.VERBOSE)
'''
:var POLY_TERM: parse polynomial terms
'''
ALL_VARS_POLY_TERM = re.compile(
    r'''(                      # group match float in all formats
        (\d+(\.\d*)?|\.\d+)    # match numbers: 1, 1., 1.1, .1
        ([eE][-+]?\d+)?        # scientific notation: e(+/-)2 (*10^2)
        )?                     # 0 or one time

        ([a-z]+)?               # variables extracted from VAR_NAMES
                               # 0 or one time
        (\^)?                  # exponentiation 0 or one time
        (\d+)?                 # exponent 0 or one time
        '''.format(''.join(VAR_NAMES)), re.VERBOSE)


def get_args():
    parser = argparse.ArgumentParser(
        description='{}\nvalid variables: {}'.format(
            DESCRIPTION, ', '.join(VAR_NAMES)),
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-b', '--batch', action='store_true',
        help='process equations in batch')
    parser.add_argument(
        '-i', '--input-file', action='store', default='equations.in',
        help='get the equations from this file in batch mode')
    parser.add_argument(
        '-o', '--output-file', action='store', default='equations.out',
        help='write the canonicalized equations to this file in batch mode')

    args_as_dict = vars(parser.parse_args())
    return args_as_dict


def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    rgs = get_args()

    if not rgs['batch']:

        from six.moves import input

        while True:
            equation = input('enter an equation>>> ')

            print(Equation(equation).canonicalize(), '\n')

    else:
        try:
            os.remove(rgs['output_file'])
        except:
            pass

        with open(rgs['input_file'], 'r') as fh:
            equations = fh.readlines()

        for equation in equations:
            Equation(equation).canonicalize_to_file(rgs['output_file'])


class NoEquationError(Exception):
    '''
    raise when there is no equation to process
    '''
    pass


class InvalidEquationError(Exception):
    '''
    raise if there is stuff not matching POLY_VALID
    '''
    pass


class InvalidTermInEquationError(Exception):
    '''
    raised when a polynomial term does not respect the rules
    '''
    pass


class UnexpectedVariableNamesError(Exception):
    '''
    raise when an unexpected varaible name is used
    '''
    pass


def process_term(token):
    '''
    prepare a polynomial term for symbolic computation

    the re.match will return 7 groups:

        * group 0 is the coefficient

        * group 4 is the variable or product of variables (x or xy)

        * group 5 is the exponentiation

        * group 6 is the exponent
    '''
    coefficient = ''
    exponentiation = ''
    variables = ''
    term = re.match(POLY_TERM, token)

    # TODO: to detect variable names that we don't know about, we repeat the
    # match but with an all chars pattern in the variables group
    # begs the question: what happens with multichar variable names?
    # this is where implicit multiplication bites us; were it not permitted
    # this would never manifest itself
    no_term = re.match(ALL_VARS_POLY_TERM, token)
    if no_term.groups()[4] and not term.groups()[4]:
        # we have variables but they're unknown, grrrr
        raise UnexpectedVariableNamesError(
            'unexpected variable in term %s. accepted variable names are: %s' % (token, ', '.join(VAR_NAMES)))

    if term.groups()[5] and not term.groups()[6]:
        raise InvalidTermInEquationError(
            'exponentiation with no exponent in term %s' % term)

    if term.groups()[5] and term.groups()[6]:
        # use ** to force Python syntax
        exponentiation = '**{}'.format(term.groups()[6])

    if term.groups()[0] and not term.groups()[4]:
        coefficient = term.groups()[0]
        return coefficient

    if term.groups()[0] and term.groups()[4]:
        # expand implicit multiplication between coefficient and variable
        coefficient = '{}*'.format(term.groups()[0])

    if term.groups()[4]:
        if Counter(
                [var_name in term.groups()[4] for
                 var_name in VAR_NAMES])[True] == 1:
            variables = term.groups()[4]

        if Counter(
                [var_name in term.groups()[4] for
                 var_name in VAR_NAMES])[True] > 1:
            # we have a multivariable term here and we need to expand the
            # implicit multiplication between vars
            # Counter returns a dictionary {True: #inlist, False: #notinlist}
            variables = '*'.join(
                [var_name for var_name in VAR_NAMES
                 if var_name in term.groups()[4]])

    return '{}{}{}'.format(coefficient, variables, exponentiation)


class Equation(object):
    '''
    represnts an equation
    '''

    def __init__(self, equation=None):
        '''
        :arg str equation:
        '''
        if equation is None:
            raise NoEquationError('must provide an equation')

        if not isinstance(equation, six.text_type):
            # not a string? coerce it
            # use six.text_type to handle both python 2 and python 3
            equation = str(equation)

        self.equation = equation

        self._validate_equation()
        self._sanitize_equation()

        self.left_hand_side, self.right_hand_side = self._process_equation(
        ).split('=')

    def canonicalize(self):
        '''
        returns the canonical form of the equation

        also convert to the required syntax: implicit multiplication and ^ for
        power ops
        '''
        ret = '{} = 0'.format(
            simplify(
                sympify(self.left_hand_side) - sympify(self.right_hand_side)))
        return ret.replace('**', '^').replace('*', '')

    def canonicalize_to_file(self, file_name):
        '''
        canonicalize to file 
        wrtie mode is append
        '''
        with open(file_name, 'a') as fh:
            fh.write('{}\n'.format(self.canonicalize()))

    def _process_equation(self):
        '''
        rebuild the equation after validating each term

        this is where we expand implied multiplications and use correct
        Python syntax for exponentiation
        '''
        processed_equation = ''

        for token in re.split(POLY_SPLIT, self.equation):
            if not token:
                continue
            if token in ['+', '-', '=', '(', ')', '[', ']', '{', '}']:
                processed_equation += token
                continue

            # now it gets interesting
            processed_equation += process_term(token)

        return processed_equation

    def _sanitize_equation(self):
        '''
        replace Python style exponentiation (**) with caret (^); we will
        revert that later

        remove white space
        #TODO: all white space, not just spaces

        remove explicit multiplication, it makes parsing easier; we will
        revert that later as well
        '''
        self.equation = self.equation.replace('**', '^')
        self.equation = self.equation.replace('*', '')
        self.equation = self.equation.replace(' ', '')

    def _validate_equation(self):
        '''
        there are some characters or character combinations that are just not
        allowed
        '''
        if not re.match(POLY_VALID, self.equation):
            raise InvalidEquationError(
                'bad characters in equation %s' % self.equation)

        if self.equation.count('=') > 1:
            raise InvalidEquationError(
                'cannot have more than one = sign in equation %s'
                % self.equation)

        if self.equation.count('++'):
            raise InvalidEquationError(
                'repeated + sign in equation %s' % self.equation)

        if self.equation.count('--'):
            raise InvalidEquationError(
                'repeated - sign in equation %s' % self.equation)

        if self.equation.count('+-') or self.equation.count('-+'):
            raise InvalidEquationError(
                '+- or -+ sign combination in equation %s' % self.equation)

        if self.equation.count('^^'):
            raise InvalidEquationError(
                'unknown operation ^^ in equation %s' % self.equation)

        if self.equation.count('***'):
            raise InvalidEquationError(
                'unknown operation *** in equation %s' % self.equation)


if __name__ == "__main__":
    main()
