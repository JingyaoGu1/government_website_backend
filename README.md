# Central signup backend app

This app demonstrates how to log in using the Auth0 Universal Page, and call a backend API using an access token.

## Installation

After cloning the repository, run:

```bash
$ pip install -r requirements.txt
```

This will install the necessary packages in order for the sample to run.

## Running the Application

To start the app from the terminal, run:

```bash
$ python server.py
```

Open the application in the browser at [http://localhost:3000](http://localhost:3000). Use other ports when port 3000 is being used! Try localhost:3001

## User signup validation

Call POST http://localhost:3000/signup with user information in request body to signup.

```
{
  "Email": "example1@email.com",
  "Password": "DSAJIOdjsaio123()*)",
  "First Name": "John",
  "Middle Name": "Doe",
  "Last Name": "Smith",
  "SSN": "123-45-6789",
  "Address Line 1": "123 Main St",
  "Address Line 2": "Apt 4B",
  "City": "Jersey City",
  "State": "NJ",
  "Zipcode": "07302"
}
```
The backend app will validate the user information during the registration.
- If there are missing fields or some field format are incorrect, the signup will be failed.
- If the "City" and "State" are not matched with "zipcode", the signup will be succeed, but the "Address Mismatch" will be 1; otherwise it should be 0.

## Support three search methods:
- first name
  - input Leo in first name inbox —> show all users whose first name is Leo
- last name
- state
  - input New York in City inbox —> show all users whose city is New York

It will show user information as a list (part of user information).

## Support user log information search:

If we click the `View` button in user `Account History` column, the user log table will be displayed below.