const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const bcrypt = require('bcrypt');
const ejs = require('ejs');
const axios = require('axios');
const cookie = require('cookie');
const querystring = require('querystring');
const app = express();
const port = process.env.PORT || 3000;

const compiler_url = "http://compiler-service:5000";
const admin_url = "http://192.168.55.102:31000";

app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));
app.set('view engine', 'ejs');

app.use(session({
    secret: 'secret',
    resave: true,
    saveUninitialized: true
}));


const mysql = require('mysql2/promise');

// Create a connection pool
const pool = mysql.createPool({
    host: 'database.c5zjm2epqrko.ap-south-1.rds.amazonaws.com',
    user: 'admin',
    password: 'Admin123',
    database: 'onlinejudge'
});

app.get('/', async (req, res) => {
    if (!req.session.userId) {
        return res.redirect('/login');
    }

    try {
        // Find the user with the given ID
        const [rows] = await pool.query('SELECT username FROM app_customuser WHERE id = ?', [req.session.userId]);

        if (rows.length === 0) {
            return res.redirect('/login');
        }

        const username = rows[0].username;
        req.session.username = username;


        const response = await axios.get(admin_url+'/problems?format=json');
        const questions = response.data;
        res.render('home', { username: username, questions: questions })


    } catch (error) {
        console.error(error);
        res.redirect('/login');
    }
});


app.get('/register', (req, res) => {
    res.render('register')
});

app.post('/register', async (req, res) => {
    const { username, email, password } = req.body;

    const hashedPassword = await bcrypt.hash(password, 10);

    try {
        // Check if the username already exists
        const [rows] = await pool.query('SELECT id FROM app_customuser WHERE username = ?', [username]);

        if (rows.length > 0) {
            return res.redirect('/register');
        }

        // Insert the new user into the database
        // await pool.query('INSERT INTO app_customuser (username,email, password, is_superuser,score,solved,is_active,is_staff) VALUES (?,?, ?,?,?,?,?,?)', [username, email, hashedPassword, true, 0, 0, true, false]);
        await pool.query('INSERT INTO app_customuser (username,email, password) VALUES (?,?, ?)', [username, email, hashedPassword]);

        res.redirect('/login');
    } catch (error) {
        console.error(error);
        res.redirect('/register');
    }
});

app.get('/login', (req, res) => {
    res.render('login')
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    try {
        // Find the user with the given username
        const [rows] = await pool.query('SELECT id, password FROM app_customuser WHERE username = ?', [username]);

        if (rows.length === 0) {
            return res.redirect('/login');
        }

        const user = rows[0];
        const isValidPassword = await bcrypt.compare(password, user.password);

        if (!isValidPassword) {
            return res.redirect('/login');
        }

        // Set the user ID in the session
        req.session.userId = user.id;

        res.redirect('/');
    } catch (error) {
        console.error(error);
        res.redirect('/login');
    }
});


app.get('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            return res.redirect('/');
        }

        res.clearCookie('connect.sid');
        res.redirect('/login');
    });
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});



app.get('/ide/:id', async (req, res) => {

    if (!req.session.userId) {
        return res.redirect('/login');
    }

    try {
        const response = await axios.get(admin_url+`/problems/${req.params.id}?format=json`); // fetch the JSON data from the URL
        const questions = response.data; // extract the JSON data from the response
        // console.log(questions)
        let previous_submission ='';
        const [submissions] = await pool.query(`SELECT * FROM app_submissions WHERE result = 'Accepted'AND problem_id = ${req.params.id} AND user_id = ${req.session.userId} ORDER BY id DESC LIMIT 1`);
        if (submissions.length != 0) {
            previous_submission = submissions[0].previous_submission;
        }

        res.render('ide', { previous_submission: previous_submission, username: req.session.username, userId: req.session.userId, questions: questions });
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching JSON data'); // handle any errors that occur
    }
    // res.render('ide')
});

app.get('/problem/:id', async (req, res) => {
    if (!req.session.userId) {
        return res.redirect('/login');
    }

    try {
        const response = await axios.get(admin_url+`/problems/${req.params.id}?format=json`); // fetch the JSON data from the URL
        const questions = response.data; // extract the JSON data from the response
        // console.log(questions)
        res.render('problem', { username: req.session.username, questions: questions });
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching JSON data'); // handle any errors that occur
    }

    // res.render('problem')
});
app.get('/submissions/:id', async (req, res) => {

    if (!req.session.userId) {
        return res.redirect('/login');
    }

    try {
        const response = await axios.get(admin_url+`/submissions/problem/${req.params.id}?format=json`); // fetch the JSON data from the URL
        const submissions = response.data; // extract the JSON data from the response
        const [arr] = await pool.query('SELECT id, username FROM app_customuser ;');
        // console.log(arr)
        const dict = arr.reduce((acc, curr) => {
            const id = parseInt(curr.id);
            acc[id] = curr.username;
            return acc;
        }, {});

        // console.log(questions)
        res.render('submissions', { username: req.session.username, submissions: submissions, quesId: req.params.id, users: dict });
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching JSON data'); // handle any errors that occur
    }
});

app.post('/run_code', async (req, res) => {
    const data = req.body;
    try {
        const response = await axios.post(compiler_url+`/run_code`, data); // fetch the JSON data from the URL
        console.log(response.data)
        output = "Run Time = " + response.data.run_time  + "\n" + response.data.result
        return res.send(output)
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching JSON data'); // handle any errors that occur
    }
});



app.post('/submit_code', async (req, res) => {
    const data = req.body;
    // console.log(data)
    const response = await axios.get(admin_url+ `/problems/${data.problem_id}?format=json`); // fetch the JSON data from the URL
    const problem = response.data;
    // console.log(problem)
    const [kk] = await pool.query('SELECT input, output FROM app_testcases WHERE problem_id = ?', [problem.id]);
    data['test_cases'] = kk
    // console.log(data)
    data['time_limit'] = problem.time_limit;
    // console.log(data)
    const Jsondata = JSON.stringify(data);
    // console.log(Jsondata)
    try {
        const response = await axios.post(compiler_url+`/submit_code`, Jsondata, {
            headers: {
                'Content-Type': 'application/json'
            }
        }); // fetch the JSON data from the URL
        output = response.data
        // console.log(output)
        if (output === "Accepted") {
            const [rows] = await pool.query('SELECT * FROM app_customuser WHERE id = ?', [req.session.userId]);
            const user = rows[0];
            // console.log(user)
            const solved = user.solved + 1
            const score = user.score + problem.score
            // user table update user data for score and solved count
            await pool.query(`UPDATE app_customuser SET score = ${score}, solved = ${solved} WHERE id = ${req.session.userId}`);

            // insert into submissions table
            const [ll] = await pool.query('SELECT * FROM app_submissions');
            // console.log(ll)
            
            await pool.query('INSERT INTO app_submissions (result,previous_submission, language, problem_id, user_id,date_created) VALUES (?,?,?,?,?,?)', [output,data['code'],data['language'],data['problem_id'],data['user_id'],new Date()]);

            return res.send(output)
        } else {
             //on solution fail
             await pool.query('INSERT INTO app_submissions (result,previous_submission, language, problem_id, user_id,date_created) VALUES (?,?,?,?,?,?)', ["Failed",data['code'],data['language'],data['problem_id'],data['user_id'],new Date()]);
             //
            return res.send(output)
        }
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching JSON data'); // handle any errors that occur
    }
});

