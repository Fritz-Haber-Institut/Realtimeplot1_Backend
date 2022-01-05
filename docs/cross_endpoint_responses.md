# Cross-endpoint responses <!-- omit in toc -->

## Table of contents <!-- omit in toc -->
- [Access-Tokens](#access-tokens)
- [Non-existent resources](#non-existent-resources)
- [Bad requests (JSON in the request body)](#bad-requests-json-in-the-request-body)

## Access-Tokens

Some endpoints require access tokens (generatable with [/auth/get_access_token](endpoints/auth.md#authget_access_token)) to be accessed. These endpoints can also return the following server responses:

Server response (403 FORBIDDEN): *Invalid access-token*
```
INVALID ACCESS-TOKEN
```

> Additional information is stored in the Authentication header.
> - invalid access_token

Server response (401 UNAUTHORIZED): *Missing access-token*
```
MISSING ACCESS-TOKEN
```

> Additional information is stored in the Authentication header.
> - missing access_token

## Non-existent resources

Endpoints that are supposed to return individual resources return 404 if the queried resource does not exist in the database.

Server response (404 NOT FOUND): *Non-existent resource*

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try
	again.</p>
```

## Bad requests (JSON in the request body)

If an endpoint expects JSON in the body, the server can respond to incorrectly submitted data in the body in the following ways:

Server response (400 BAD REQUEST) *null was set as value for a key*
```
VALUES MUST NOT BE null
```

Server response (400 BAD REQUEST) *Data was not submitted as JSON*
```
DATA MUST BE PROVIDED IN THE BODY AS JSON
```