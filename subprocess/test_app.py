import unittest
from app import run_python,run_javascript


class TestRunPython(unittest.TestCase):

    def test_run_python_with_valid_input(self):
        code = "print('hello world')"
        input_ = ''
        expected_output = 'hello world\n'
        result = run_python(code, input_)
        self.assertEqual(result, expected_output)

    def test_run_python_with_invalid_input(self):
        code = "1/0"
        input_ = ''
        expected_error = 'ZeroDivisionError: division by zero\n'
        result = run_python(code, input_)
        error_lines = result.split('\n')
        self.assertEqual(error_lines[-2], expected_error.strip())

    def test_run_javascript_with_valid_input(self):
        code = 'console.log("Hello world!")'
        input_ = ''
        expected_output = 'Hello world!\n'
        
        result = run_javascript(code, input_)
        self.assertEqual(result, expected_output)

    def test_run_javascript_with_invalid_input(self):
        code = "console.log(x);"
        input_ = ""
        expected_error = "ReferenceError: x is not defined"
        result = run_javascript(code, input_)
        error_lines = result.split('\n')
        for line in error_lines:
            if 'ReferenceError' in line:
                error_message = line.strip()
                break

        self.assertEqual(error_message, expected_error.strip())

if __name__ == '__main__':
    unittest.main()
