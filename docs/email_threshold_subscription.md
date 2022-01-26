# Email threshold subscription <!-- omit in toc -->

## Table of contents <!-- omit in toc -->
- [Database models](#database-models)
  - [Subscription](#subscription)
- [Endpoints](#endpoints)
  - [Subscribe to process variable thersholds](#subscribe-to-process-variable-thersholds)
    - [RESPONSE 200 OK](#response-200-ok)
    - [RESPONSE 400 BAD REQUEST - Missing attributes](#response-400-bad-request---missing-attributes)
    - [RESPONSE 400 BAD REQUEST - thresholds not sent as integers](#response-400-bad-request---thresholds-not-sent-as-integers)
  - [Unsubscribe from process variable thersholds](#unsubscribe-from-process-variable-thersholds)
    - [RESPONSE 200 OK](#response-200-ok-1)

## Database models

### Subscription

| Column name   | type                                     | primary key | unique | nullable | default value            |
|---------------|------------------------------------------|-------------|--------|----------|--------------------------|
| user_id       | ForeignKey("user.user_id")               | True        | False  | False    | ---                      |
| pv_string     | ForeignKey("process_variable.pv_string") | True        | False  | False    | ---                      |
| email         | db.String(100)                           | True        | False  | False    | user.email               |
| threshold_min | db.Integer                               | False       | False  | False    | pv.default_threshold_min |
| threshold_max | db.Integer                               | False       | False  | False    | pv.default_threshold_max |

*The combination of `user_id`, `pv_string`, and `email` may only exist once in the database.*

## Endpoints

### Subscribe to process variable thersholds

- Endpoint: `/email/subscribe/<pv_string>`
- Method: `POST`

*Send an access token in the "x-access-tokens" header that is related to a user in the experiment!*

```JSON
{
    "email": "...",
    "threshold_min": ...,  # int
    "threshold_max": ...   # int
}
```

- *`email` is optional if an email is assigned to the user*
- *`threshold_min` is optional if `default_threshold_min` is set in the process variable*
- *`threshold_max` is optional if `default_threshold_max` is set in the process variable*

#### RESPONSE 200 OK
```JSON
{
    "subscription": {
        "email": "...",
        "pv_string": "...:...:...",
        "threshold_max": ...,   # int
        "threshold_min": ...,   # int
        "user_id": "..."
    }
}
```

***Attention:** If the user's email is changed, the subscription **will not be automatically adjusted**. Either the frontend has to do this automatically by **calling the endpoints to unsubscribe and subscribe**, or the user has to do this manually.*

#### RESPONSE 400 BAD REQUEST - Missing attributes 
```JSON
{
    "errors": [
        [
            "email: Missing email."
        ],
        [
            "threshold_min: Missing threshold_min."
        ],
        [
            "threshold_max: Missing threshold_max."
        ]
    ]
}
```

#### RESPONSE 400 BAD REQUEST - thresholds not sent as integers
```JSON
{
    "errors": [
        "threshold_min and threshold_max must be integers."
    ]
}
```

*Only integers or integers as strings are accepted.*

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests that try to add already existing objects to the database](cross_endpoint_responses.md#responses-for-requests-that-try-to-add-already-existing-objects-to-the-database)!

Also check out: [Responses to requests that result in server-side communication with another MQTT server](cross_endpoint_responses.md#responses-to-requests-that-result-in-server-side-communication-with-another-mqtt-server)!

Also check out: [Responses for requests that call endpoints that can only be called by users assigned to the queried experiments](cross_endpoint_responses.md#responses-for-requests-that-call-endpoints-that-can-only-be-called-by-users-assigned-to-the-queried-experiments)!

### Unsubscribe from process variable thersholds

- Endpoint: `/email/subscribe/<pv_string>`
- Method: `DELETE`

#### RESPONSE 200 OK
```JSON
{
    "message": "Successfully deleted subscription (user_id=...,pv_string=...)"
} 
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

Also check out: [Responses for requests which delete database objects](cross_endpoint_responses.md#responses-for-requests-which-delete-database-objects)!

Also check out: [Responses to requests that result in server-side communication with another MQTT server](cross_endpoint_responses.md#responses-to-requests-that-result-in-server-side-communication-with-another-mqtt-server)!