# Import the required modules
import mysql.connector
from flask import Flask, jsonify, request
import subprocess
import time
# Create a Flask app
app = Flask(__name__)

# Connect to the MySQL database
db = mysql.connector.connect(
    host='database.c5zjm2epqrko.ap-south-1.rds.amazonaws.com',
    user= 'admin',
    password= 'Admin123',
    database= 'onlinejudge'
)



# Create a cursor object
cursor = db.cursor()

def run_python(code,input_):
    result = subprocess.run(['python', '-c', code], input=input_, capture_output=True)
    output = result.stdout.decode('utf-8')
    error = result.stderr.decode('utf-8')

    if error:
        return error
    else:
        return output

def run_c(code,input_):
    result = subprocess.run(['gcc', '-x', 'c', '-o', 'program', '-'], input=code, capture_output=True)
    output = result.stdout.decode('utf-8')
    error = result.stderr.decode('utf-8')

    if error:
        return error
    else:
        # Run the compiled program in a subprocess
        result = subprocess.run(['./program'], input=input_, capture_output=True)
        output = result.stdout.decode('utf-8')
        return output

def run_cpp(code,input_):
    # Compile the program
    result = subprocess.run(['g++', '-x', 'c++', '-o', 'program', '-'], input=code, capture_output=True)
    if result.returncode != 0:
        return result.stderr.decode('utf-8')

    # Execute the program with custom input
    result = subprocess.run(['./program'], input=input_, capture_output=True)
    output = result.stdout.decode('utf-8')

    return output

def run_javascript(code,input_):
    cmd = ['node', '-e', code]
    result = subprocess.run(cmd, input=input_, capture_output=True)
    output = result.stdout.decode('utf-8')
    error = result.stderr.decode('utf-8')

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

def Submit(code,language,problem_id,user_id):
    cursor.execute("SELECT * FROM app_problem WHERE id = %s", (problem_id,))
    problem = cursor.fetchall()
    cursor.execute("SELECT * FROM app_customuser WHERE id = %s", (user_id,))
    user = cursor.fetchall()
    cursor.execute("SELECT * FROM app_testcases WHERE id = %s", (problem_id,))
    test_cases = cursor.fetchall()

    length_test_cases = len(test_cases)
    
    test_cases = []
    for input_ in test_cases:
        Result = Run(code, language,input_.input)
        # print(input_.output.encode('utf-8'))
        input_.output = input_.output.encode('utf-8')
        # print(Result['result'][:].encode('utf-8'))
        result_ = Result['result']
        Result['result'] = Result['result'][:].encode('utf-8')
        if 'Error' in result_:
            out = 'Runtime Error in test case ' + str(len(test_cases) - length_test_cases) + '\n' + result_
        elif Result['result'] == input_.output and Result['run_time'] <= problem.time_limit:
            length_test_cases -= 1
        elif Result['result'] == input_.output and Result['run_time'] > problem.time_limit:
            out = 'Time Limit Exceeded on test case ' + str(len(test_cases) - length_test_cases)
        else:
            out = 'Wrong Answer on test case ' + str(len(test_cases) - length_test_cases) 
            break
    if length_test_cases == 0:
        out = 'Accepted'
    #     solved = user.solved +1
    #     score = user.score + problem.score
    #     user.solved = solved
    #     user.score = score
    #     user.save()


    # submission = Submissions.objects.create(user=user,problem=problem,language=language,result=out,previous_submission=code)
    # submission.save()

    return out




@app.route("/submit_code", methods=["POST"])
def submit_code():
    data = request.json
    print(data)
    return "recived"


@app.route("/run_code", methods=["POST"])
def execute_code():
    data = request.json
    print(data)
    output = Run(data['code'].encode('utf-8'), data['language'],data['input'].encode('utf-8'))
    print(output)
    return output


    
# Run the app
if __name__ == "__main__":
    app.run(debug=True,port=5000)