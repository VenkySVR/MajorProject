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

const compiler_url = "http://compiler:5000";
const admin_url = "http://admin";

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

// app.get('/', async (req, res) => {
//     try {
//         const response = await axios.get(admin_url+'/problems?format=json'); // fetch the JSON data from the URL
//         const questions = response.data; // extract the JSON data from the response
//         // console.log(questions)
//         res.render('home', {questions: questions});
//     } catch (error) {
//         console.error(error);
//         res.status(500).send('Error fetching JSON data'); // handle any errors that occur
//     }
// });

app.get('/ide/:id', async (req, res) => {

    if (!req.session.userId) {
        return res.redirect('/login');
    }

    try {
        const response = await axios.get(admin_url+`/problems/${req.params.id}?format=json`); // fetch the JSON data from the URL
        const questions = response.data; // extract the JSON data from the response
        // console.log(questions)
        res.render('ide', { username: req.session.username, userId: req.session.userId, questions: questions });
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
    try {
        const response = await axios.post(compiler_url+`/submit_code`, data); // fetch the JSON data from the URL
        output = "Run Time = " + response.data.run_time  + "\n"+ response.data.result
        return res.send(output)
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching JSON data'); // handle any errors that occur
    }
});




















// app.get('/', async (req, res) => {
//     if (!req.session.userId) {
//         return res.redirect('/login');
//     }

//     try {
//         const response = await axios.get(admin_url+'/problems?format=json'); // fetch the JSON data from the URL
//         const questions = response.data; // extract the JSON data from the response
//         // console.log(questions)
//         res.render('home', { questions: questions });
//     } catch (error) {
//         console.error(error);
//         res.status(500).send('Error fetching JSON data'); // handle any errors that occur
//     }
// });


// app.post('/register', async (req, res) => {
//     const postData = querystring.stringify(req.body);

//     try {
//         // Check if the username already exists
//         const response = await axios.post(admin_url+'/register', postData); // fetch the JSON data from the URL
//         const data = response.data; // extract the JSON data from the response
//         console.log(req.body)
//         console.log(data)

//         res.redirect('/login');
//     } catch (error) {
//         console.error(error);
//         res.redirect('/register');
//     }
// });


// app.post('/login', async (req, res) => {
//     const { username, password } = req.body;
//     const postData = querystring.stringify(req.body);
//     try {
//         const response = await axios.post(admin_url+'/login', postData); // fetch the JSON data from the URL
//         const data = response.data; // extract the JSON data from the response
//         console.log(req.body)
//         console.log(data)

//         // if (!isValidPassword) {
//         //     return res.redirect('/login');
//         // }

//         // // Set the user ID in the session
//         // req.session.userId = user.id;

//         // res.redirect('/');
//     } catch (error) {
//         // console.error(error);
//         res.redirect('/login');
//     }
// });