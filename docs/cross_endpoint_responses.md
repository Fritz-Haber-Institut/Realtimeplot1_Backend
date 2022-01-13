# Cross-endpoint responses <!-- omit in toc -->

Some endpoints share responses. These shared responses are documented here and are linked in the documentation of the individual endpoints.

## Table of contents <!-- omit in toc -->
- [Responses from endpoints that require an access token](#responses-from-endpoints-that-require-an-access-token)
	- [Response 401 UNAUTHORIZED - No access token](#response-401-unauthorized---no-access-token)
	- [Response 403 FORBIDDEN - Not an admin](#response-403-forbidden---not-an-admin)
	- [Response 403 FORBIDDEN - Invalid access token](#response-403-forbidden---invalid-access-token)
- [Responses for requests with JSON bodies](#responses-for-requests-with-json-bodies)
	- [Response 400 BAD REQUEST - No JSON in body](#response-400-bad-request---no-json-in-body)
	- [Response 400 BAD REQUEST - Wrong value format](#response-400-bad-request---wrong-value-format)
- [Responses for requests that try to add already existing objects to the database](#responses-for-requests-that-try-to-add-already-existing-objects-to-the-database)
		- [Response 409 CONFLICT - Already in database](#response-409-conflict---already-in-database)
- [Responses for requests which try to query resources that do not exist in the database](#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)
- [Responses for requests which delete database objects](#responses-for-requests-which-delete-database-objects)
	- [Response 200 OK](#response-200-ok)

## Responses from endpoints that require an access token

### Response 401 UNAUTHORIZED - No access token
```JSON
{
    "errors": [
        "Access to this resource requires a valid access-token."
    ]
}
```

### Response 403 FORBIDDEN - Not an admin
```JSON
{
    "errors": [
        "Only administrators are allowed to access this endpoint."
    ]
}
```

### Response 403 FORBIDDEN - Invalid access token
```JSON
{
    "errors": [
        "The access-token sent is invalid or no longer accepted."
    ]
}
```

## Responses for requests with JSON bodies

### Response 400 BAD REQUEST - No JSON in body
```JSON
{
    "errors": [
        "You must provide the data in the body as JSON."
    ]
}
```

### Response 400 BAD REQUEST - Wrong value format
```JSON
{
    "errors": [
        "Some or more values ​​in the JSON body were null or do not correspond to the required column type in the database."
    ]
}
```

## Responses for requests that try to add already existing objects to the database

#### Response 409 CONFLICT - Already in database
```JSON
{
    "errors": [
        "A ... (...) is already present in the database."
    ]
}
```

*The object's type (first points) and its identifier (second points) of the object are sent in the response.*

## Responses for requests which try to query resources that do not exist in the database
```JSON
{
    "errors": [
        "The ... (...) is not present in the database."
    ]
}
```

*The object's type (first points) and its identifier (second points) of the object are sent in the response.*

## Responses for requests which delete database objects

### Response 200 OK
```JSON
{
    "messages": [
        "The ... (...) was successfully deleted from the database."
    ]
}
```

*The object's type (first points) and its identifier (second points) of the object are sent in the response.*