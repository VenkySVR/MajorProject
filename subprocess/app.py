# Import the required modules
from flask import Flask, jsonify, request
import subprocess
import time
# Create a Flask app
app = Flask(__name__)


def run_python(code,input_):
    result = subprocess.run(['python3', '-c', code], input=input_,encoding="utf-8", capture_output=True)
    output = result.stdout
    error = result.stderr

    if error:
        return error
    else:
        return output

def run_c(code,input_):
    result = subprocess.run(['gcc', '-x', 'c', '-o', 'program', '-'], input=code,encoding="utf-8", capture_output=True)
    output = result.stdout
    error = result.stderr

    if error:
        return error
    else:
        # Run the compiled program in a subprocess
        result = subprocess.run(['./program'], input=input_,encoding="utf-8", capture_output=True)
        output = result.stdout
        return output

def run_cpp(code,input_):
    # Compile the program
    result = subprocess.run(['g++', '-x', 'c++', '-o', 'program', '-'], input=code,encoding="utf-8", capture_output=True)
    if result.returncode != 0:
        return result.stderr

    # Execute the program with custom input
    result = subprocess.run(['./program'], input=input_,encoding="utf-8", capture_output=True)
    output = result.stdout

    return output

def run_javascript(code,input_):
    cmd = ['node', '-e', code]
    result = subprocess.run(cmd, input=input_,encoding="utf-8", capture_output=True)
    output = result.stdout
    error = result.stderr

    if error:
        return error
    else:
        return output

def Run_time(func):
    def wrapper(*args,**kwargs):
        start = time.time()
        result_code = func(*args,**kwargs)
        end = time.time()
        run_time = end-start
        result = {'result':result_code,'run_time':run_time}
        return result
    return wrapper

def run_code(code, language,input_):
    if language == 'c':
        return run_c(code, input_)
    elif language == 'cpp':
        return run_cpp(code, input_)
    elif language == 'python':
        return run_python(code, input_)
    elif language == 'javascript':
        return run_javascript(code, input_)

@Run_time
def Run(code,language,input_):
    return run_code(code,language,input_)

def Submit(code,language,test_cases,time_limit):

    length_test_cases = len(test_cases)
    out = ""
    for input_ in test_cases:
        Result = Run(code, language,input_['input'])
        input_['output'] = input_['output'].encode('utf-8')
        result_ = Result['result']
        Result['result'] = Result['result'][:-1].encode('utf-8')
        print(Result['result'])
        print(input_['output'])
        if 'Error' in result_:
            out = 'Runtime Error in test case ' + str(len(test_cases) - length_test_cases) + '\n' + result_
        elif Result['result'] == input_['output'] and Result['run_time'] <= time_limit:
            length_test_cases -= 1
        elif Result['result'] == input_['output'] and Result['run_time'] > time_limit:
            out = 'Time Limit Exceeded on test case ' + str(len(test_cases) - length_test_cases)
        else:
            out = 'Wrong Answer on test case ' + str(len(test_cases) - length_test_cases) 
            break
    if length_test_cases == 0:
        out = 'Accepted'
    return out




@app.route("/submit_code", methods=["POST"])
def submit_code():
    data = request.json
    output = Submit(data['code'], data['language'],data['test_cases'],data['time_limit'])
    return output


@app.route("/run_code", methods=["POST"])
def execute_code():
    data = request.json
    output = Run(data['code'], data['language'],data['input'])
    return output


    
# Run the app
if __name__ == "__main__":
    app.run(debug=True,port=5000)