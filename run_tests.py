import unittest
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.getcwd())

from tests.test_orb_strategy import TestOrbStrategy

if __name__ == '__main__':
    with open('test_results.txt', 'w') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        suite = unittest.TestLoader().loadTestsFromTestCase(TestOrbStrategy)
        result = runner.run(suite)
        if not result.wasSuccessful():
            sys.exit(1)
