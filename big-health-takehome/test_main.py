import argparse
import pytest
import main

def func(x):
    return x + 1


def test_args():
    with pytest.raises(SystemExit):
        main.create_args(['str'])
    with pytest.raises(SystemExit):
        main.create_args([])
    main.create_args(['5'])

def test_calculator():
    calc = main.SlidingAverageCalculator(3)
    avg = calc.add_temp(30.0)
    assert avg == 30.0
    avg = calc.add_temp(50.0)
    assert avg == 40.0
    avg = calc.add_temp(70.0)
    assert avg == 50.0
    avg = calc.add_temp(90.0)
    assert avg == 70.0