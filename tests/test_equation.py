'''unit tests'''
import os
import sys

import pytest

# modules under test are one directory up, make sure python can find them
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import equation


class TestEquation(object):
    '''
    unit tests for :class:`<equation.Equation>`
    '''
    @pytest.mark.parametrize(
        'test_id,test_input,expected_result',
        [('general>>> ', "x^2 + 3.5xy + y = y^2 - xy + y",
          "x^2 + 4.5xy - y^2 = 0"),
         ('identity>>> ', "x = 1", "x - 1 = 0"),
         ('simplify>>> ', "x - (y^2 - x) = 0", "2x - y^2 = 0"),
         ('tricky>>> ', "x - (0 - (0 - x)) = 0", "0 = 0"),
         ('python_syntax>>> ', "x**2 + 3.5*x*y + y = y**2 - x*y + y",
          "x^2 + 4.5xy - y^2 = 0"),
         ('mixed_syntax>>> ', "x^2 + 3.5xy + y = y**2 - x*y + y",
          "x^2 + 4.5xy - y^2 = 0")])
    def test_canonicalize(self, test_id, test_input, expected_result):
        assert equation.Equation(test_input).canonicalize() == expected_result

    def test_no_input_raises(self):
        with pytest.raises(equation.NoEquationError) as error:
            equation.Equation()

        assert 'must provide an equation' in error.value.args[0]

    @pytest.mark.parametrize(
        'test_id,term,expected',
        [
            ('int_coeff', '66', '66'),
            ('float_coeff', '66.66', '66.66'),
            ('scientific_coeff', '66e10', '66e10'),
            ('multivar', 'xyz', 'x*y*z'),
            ('sci_coeff_var_exp', '66e10x^23', '66e10*x**23')])
    def test_process_term(self, test_id, term, expected):
        assert equation.process_term(term) == expected

    @pytest.mark.parametrize(
        'test_id,variables',
        [('mixed', '23az'),
         ('fully_unknown', '23a^3'), ])
    def test_process_term_bad_var_raises(self, test_id, variables):
        with pytest.raises(equation.UnexpectedVariableNamesError) as error:
            equation.process_term(variables)

        assert 'unexpected variable' in error.value.args[0]

    def test_process_term_bad_exp(self):
        with pytest.raises(equation.InvalidTermInEquationError) as error:
            equation.process_term('23x^')

        assert 'no exponent' in error.value.args[0]

    @pytest.mark.parametrize(
        'test_id,test_input',
        [('double_eq', "x^2 + 3.5xy + y == y^2 - xy + y"),
         ('two_eq', "x^2 + 3.5xy + y = y^2 - xy + y = x"),
         ('three_eq', "x^2 + 3.5xy + y = y^2 - xy + y = x = x"), ])
    def test_multi_equal_equation(self, test_id, test_input):
        with pytest.raises(equation.InvalidEquationError) as error:
            equ = equation.Equation(test_input)

        assert 'more than one =' in error.value.args[0]

    @pytest.mark.parametrize(
        'test_id,test_input',
        [('plus_plus', "x^2 ++ 3.5xy + y = y^2 - xy + y"),
         ('minus_minus', "x^2 + 3.5xy + y = y^2 -- xy + y"), ])
    def test_multi_sign_equation(self, test_id, test_input):
        with pytest.raises(equation.InvalidEquationError) as error:
            equ = equation.Equation(test_input)

        assert 'repeated' in error.value.args[0]

    @pytest.mark.parametrize(
        'test_id,test_input',
        [('plus_minus', "x^2 +- 3.5xy + y = y^2 - xy + y"),
         ('minus_plus', "x^2 + 3.5xy + y = y^2 -+ xy + y"), ])
    def test_multi_sign_equation(self, test_id, test_input):
        with pytest.raises(equation.InvalidEquationError) as error:
            equ = equation.Equation(test_input)

        assert '+- or -+ sign combination' in error.value.args[0]
