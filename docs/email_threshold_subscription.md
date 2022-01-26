# Email threshold subscription <!-- omit in toc -->

## Table of contents <!-- omit in toc -->
- [Database models](#database-models)
  - [Subscription](#subscription)
- [Endpoints](#endpoints)
  - [Subscribe to process variable thersholds](#subscribe-to-process-variable-thersholds)
    - [RESPONSE 200 OK](#response-200-ok)
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

#### RESPONSE 200 OK
```JSON
{
    "message": "Successfully deleted subscription (user_id=...,pv_string=...)"
} 
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests that try to add already existing objects to the database](cross_endpoint_responses.md#responses-for-requests-that-try-to-add-already-existing-objects-to-the-database)!

Also check out: [Responses to requests that result in server-side communication with another MQTT server](cross_endpoint_responses.md#responses-to-requests-that-result-in-server-side-communication-with-another-mqtt-server)!

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