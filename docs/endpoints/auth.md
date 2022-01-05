# Auth (Authentication)  <!-- omit in toc -->

## Table of contents <!-- omit in toc -->
- [`/auth/get_access_token`](#authget_access_token)
  - [POST: send **BASIC AUTH** **username** and **password** in the **authorization header**](#post-send-basic-auth-username-and-password-in-the-authorization-header)
- [`auth/users`](#authusers)
  - [GET: send **access-token** in the **x-access-tokens header**](#get-send-access-token-in-the-x-access-tokens-header)
  - [POST: send **access-token** in the **x-access-tokens header** and **JSON in body**](#post-send-access-token-in-the-x-access-tokens-header-and-json-in-body)
- [`auth/users/user_id`](#authusersuser_id)
  - [GET: send **access-token** in the **x-access-tokens header**](#get-send-access-token-in-the-x-access-tokens-header-1)
  - [PUT: send **access-token** in the **x-access-tokens header and **JSON in body**](#put-send-access-token-in-the-x-access-tokens-header-and-json-in-body)
  - [DELETE: send **access-token** in the **x-access-tokens header**](#delete-send-access-token-in-the-x-access-tokens-header)

## `/auth/get_access_token`

### POST: send **BASIC AUTH** **username** and **password** in the **authorization header**

Server response (200 OK): *User in database*
```json
{
    "access_token": "eyJ..."
}
```

Server response (403 FORBIDDEN): *Unknown credentials*
```
FORBIDDEN
```

> Additional information is stored in the Authentication header.
> - Invalid combination of login_name and password


Server response (401 UNAUTHORIZED): *No credentials*
```
UNAUTHORIZED
```

> Additional information is stored in the Authentication header.
> - login_name and password required

## `auth/users`

### GET: send **access-token** in the **x-access-tokens header**

Server response (200 OK): *access-token belongs to an admin*
```json
{
  "users": [
    {
      "email": "first@email.example",
      "first_name": "admin",
      "last_name": "admin",
      "login_name": "admin",
      "url": "/auth/users/0",
      "user_type": "Admin"
    },
    {
      "email": "second@email.example",
      "first_name": "Max",
      "last_name": "Muster",
      "login_name": "maxmuster",
      "url": "/auth/users/d6d099a2-fc15-4585-b748-dfd27034ce5f",
      "user_type": "User"
    },
  ]
}
```

[See also "access-tokens"](docs/../../cross_endpoint_responses.md#access-tokens)

### POST: send **access-token** in the **x-access-tokens header** and **JSON in body**

```json
{
    "email": "new@email.example",
    "login_name": "maxmuster",
    "first_name": "Max",
    "last_name": "Muster",
    "user_type": "User"
}
```

> Possible values for user_type:
> - Admin
> - User

Server response (200 OK): *access-token belongs to an admin*
```json
{
    "email": "new@email.example",
    "first_name": "Max",
    "last_name": "Muster",
    "login_name": "maxmuster2",
    "temporary_password": "979a36a4-7c26-4c21-8bbe-3aaecc55cf95",
    "url": "/auth/users/d09f74c7-20dd-4c37-b5f7-ef0b11e22e5e",
    "user_type": "User"
}
```

> The password should be changed immediately by the user.

Server response (409 CONFLICT): *User (login_name) already exists*
```
USER ALREADY EXISTS
```

[See also "access-tokens"](docs/../../cross_endpoint_responses.md#access-tokens)

[See also "bad-requests-json-in-the-request-body"](docs/../../cross_endpoint_responses.md#bad-requests-json-in-the-request-body)

## `auth/users/user_id`

### GET: send **access-token** in the **x-access-tokens header**

Server response (200 OK): *access-token belongs to an admin or the user with the accessed user_id*
```json
{
    "email": "new@email.example",
    "first_name": "Max",
    "last_name": "Muster",
    "login_name": "maxmuster",
    "user_type": "User"
}
```

[See also "access-tokens"](docs/../../cross_endpoint_responses.md#access-tokens)

[See also "non-existent-resources"](docs/../../cross_endpoint_responses.md#non-existent-resource)

### PUT: send **access-token** in the **x-access-tokens header and **JSON in body**
```json
{
    "email": "",
    "password": "super-secure-passphrase"
}
```

> - To remove the email send an empty string!
> - Send only the keys that should be changed!
> - The server will ignore unknown keys.
> - The server will ignore the user_type key without an error message if the used access-token does not belong to an admin.

Server response (200 OK): *access-token belongs to an admin or the user with the accessed user_id*
```json
{
    "email": "",
    "first_name": "Max",
    "last_name": "Muster",
    "login_name": "maxmuster",
    "user_type": "User"
}
```

Server response (400 BAD REQEST): *email has an invalid format or invalid user_type*
```json
{
    "errors": [
        "email: invalidemail is not a valid email address",
        "user_type: 'Test' is not a valid UserTypeEnum"
    ]
}
```

[See also "access-tokens"](docs/../../cross_endpoint_responses.md#access-tokens)

[See also "non-existent-resources"](docs/../../cross_endpoint_responses.md#non-existent-resource)

[See also "bad-requests-json-in-the-request-body"](docs/../../cross_endpoint_responses.md#bad-requests-json-in-the-request-body)

### DELETE: send **access-token** in the **x-access-tokens header**

Server response (200 OK): *access-token belongs to an admin or the user with the accessed user_id*
```
USER maxmuster SUCCESSFULLY DELETED
```

Server response (409 CONFLICT): *No admin after deletion*
```
admin IS THE ONLY REGISTERED ADMIN AND THEREFORE CANNOT BE DELETED
```

[See also "access-tokens"](docs/../../cross_endpoint_responses.md#access-tokens)

[See also "non-existent-resources"](docs/../../cross_endpoint_responses.md#non-existent-resource)

