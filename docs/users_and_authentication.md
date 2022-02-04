# Users and authentication  <!-- omit in toc -->

Users can authenticate themselves to the server to be able to access resources.

## Table of contents  <!-- omit in toc -->
- [Database models](#database-models)
  - [User](#user)
- [Endpoints](#endpoints)
  - [Obtaining an access token](#obtaining-an-access-token)
    - [Response 200 OK - Valid credentials](#response-200-ok---valid-credentials)
    - [Response 401 UNAUTHORIZED - No credentials](#response-401-unauthorized---no-credentials)
    - [Response 403 FORBIDDEN - Wrong credentials](#response-403-forbidden---wrong-credentials)
  - [Get a list of all registered users](#get-a-list-of-all-registered-users)
    - [Response 200 OK - Valid access token](#response-200-ok---valid-access-token)
  - [Create a user](#create-a-user)
    - [Response 200 OK](#response-200-ok)
    - [Response 400 BAD REQUEST - Missing columns](#response-400-bad-request---missing-columns)
  - [Get user data](#get-user-data)
    - [Response 200 OK](#response-200-ok-1)
    - [Response 404 NOT FOUND - Not in database](#response-404-not-found---not-in-database)
    - [Response 403 FORBIDDEN - Not authorised](#response-403-forbidden---not-authorised)
  - [Change user data](#change-user-data)
    - [Response OK](#response-ok)
  - [Delete user](#delete-user)
    - [Response 409 CONFLICT - Last Admin](#response-409-conflict---last-admin)

## Database models

### User

| Column name        | type                      | primary key | unique | nullable | default value |
|--------------------|---------------------------|-------------|--------|----------|---------------|
| user_id            | Text(36)                  | True        | True   | False    | uuid4 or int  |
| login_name         | String(100)               | False       | True   | False    | ---           |
| first_name         | String(100)               | False       | False  | False    | ---           |
| email              | String(100)               | False       | False  | True     | ---           |
| password_hash      | String(100)               | False       | False  | False    | ---           |
| user_type          | UserTypeEnum              | False       | False  | False    | "User"        |
| experiments        | db.backref("experiments") | False       | False  | False    | ---           |
| preferred_language | String(10)                | False       | False  | False    | "en"          |

- *The server will generate the user_id when an admin creates a user. Format: uuid4. The only exception is the admin (user_id: 0) generated automatically when the database is created.*
- *The user_type can only be "User" or "Admin".*

## Endpoints

### Obtaining an access token

- Endpoint: `auth/get_access_token`
- Method: `POST`

*Send a username (login_name) and a password in the "Authorization" header via "Basic auth"!*

#### Response 200 OK - Valid credentials

```JSON
{
    "access_token": "eyJ...",
    "user_url": "/auth/users/..."
}
```

*You can query the user's data assigned to the "access_token" via the "user_url".*

#### Response 401 UNAUTHORIZED - No credentials
```JSON
{
    "errors": [
        "Access requires authorization via login_name and password (Basic Auth)."
    ]
}
```

#### Response 403 FORBIDDEN - Wrong credentials
```JSON
{
    "errors": [
        "The login_name and password combination is not present in the database."
    ]
}
```

### Get a list of all registered users

- Endpoint: `auth/users`
- Method: `GET`

*Send an **admin** access token in the "x-access-tokens" header!*

#### Response 200 OK - Valid access token
```JSON
{
    "users": [
        {
            "email": "...",
            "experiment_urls": [
                "/experiments/ABC",
                "/experiments/DEF"
            ],
            "first_name": "...",
            "last_name": "...",
            "login_name": "...",
            "preferred_language": "...",
            "url": "/auth/users/...",
            "user_id": "...",
            "user_type": "Admin"
        },
        {
            "email": null,
            "experiment_urls": [],
            "first_name": "...",
            "last_name": "...",
            "login_name": "...",
            "preferred_language": "",
            "url": "/auth/users/...",
            "user_id": "...",
            "user_type": "User"
        }
    ]
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

### Create a user

- Endpoint: `auth/users`
- Method: `POST`

*Send an **admin** access token in the "x-access-tokens" header!*

```JSON
{
    "first_name": "Max",
    "last_name": "Muster",
    "user_type": "User",
    "login_name": "max123",
    "preferred_language": "de",
    "email": "max123@email.example"
}
```

*"preferred_language" and "email" are optional.*

#### Response 200 OK
```JSON
{
  "user": {
    "email": "max123@email.example",
    "experiment_urls": [],
    "first_name": "Max",
    "last_name": "Muster",
    "login_name": "max123",
    "preferred_language": "de",
    "temporary_password": "...",
    "url": "/auth/users/...",
    "user_id": "...",
    "user_type": "User"
  }
}
```

#### Response 400 BAD REQUEST - Missing columns
```JSON
{
    "errors": [
        "The user creation request did not contain all of the information required."
    ]
}
```

See [User](#user) for the required data!

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests that try to add already existing objects to the database](cross_endpoint_responses.md#responses-for-requests-that-try-to-add-already-existing-objects-to-the-database)!

### Get user data

- Endpoint: `auth/users/<user_id>`
- Method: `GET`

*Send an access token in the "x-access-tokens" header! The token must belong to an admin or the requested user.*

#### Response 200 OK
```JSON
{
    "user": {
        "email": "...",
        "experiment_urls": [
            "/experiments/ABC",
            "/experiments/DEF"
        ],
        "first_name": "...",
        "last_name": "...",
        "login_name": "...",
        "preferred_language": "...",
        "url": "/auth/users/...",
        "user_id": "...",
        "user_type": "..."
    }
}
```

*You can query the data of the experiments assigned to the user via the experiment_urls.*

#### Response 404 NOT FOUND - Not in database
```JSON
{
    "errors": [
        "The user (...) is not present in the database."
    ]
}
```

#### Response 403 FORBIDDEN - Not authorised
```JSON
{
    "errors": [
        "Only administrators or the user with user_id 0 can access this endpoint."
    ]
}
```

### Change user data

- Endpoint: `auth/users/<user_id>`
- Method: `PUT`

*Send an access token in the "x-access-tokens" header! The token must belong to an admin or the requested user.*

```JSON
{
  "email": "...",
  "first_name": "...",
  "last_name": "...",
  "login_name": "...",
  "user_type": "...",
  "password": "...",
  "preferred_language": "..."
}
```

*Send only the keys for the values ​​that you want to change! All data that the requesting user can change will be updated. The server ignores everything else, but error messages may be issued.*

*Users (who are not admins) must send their password via "Basic auth" in addition to the access token to be able to change their password. The username is optional. If specified, the server ensures that it is the correct username.*

*"user_type" can only be changed by admins.*

If the password key is sent in the JSON body, the user is not an admin, and the user does not additionally authorize with "Basic auth" the following error message is sent in `errors`:

```
"Basic Auth is required for non-admins."
```

#### Response OK
```JSON
{
    "errors": [
        "email: ... is not a valid email address",
        "login_name: The login_name (...) is already in use.",
        "user_type: The user_type (...) is not valid and was therefore not accepted."
    ],
    "user": {
        "email": null,
        "experiment_urls": [],
        "first_name": "...",
        "last_name": "...",
        "login_name": "...",
        "preferred_language": "...",
        "url": "/auth/users/...",
        "user_id": "...",
        "user_type": "..."
    }
}
```

The **user_type** of the **last admin** in the database must not be changed to "User". Such a request is ignored and results in the following message in `errors`:

```
"user_type: The user_type cannot be changed from 'admin' to 'user' because the user '...' is the last registered admin in the database."
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

### Delete user

- Endpoint: `auth/users/<user_id>`
- Method: `DELETE`

*Send an **admin** access token in the "x-access-tokens" header!*

#### Response 409 CONFLICT - Last Admin
```JSON
{
    "errors": [
        "The user (admin) is the only registered admin and therefore cannot be deleted."
    ]
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

Also check out: [Responses for requests which delete database objects](cross_endpoint_responses.md#responses-for-requests-which-delete-database-objects)!







