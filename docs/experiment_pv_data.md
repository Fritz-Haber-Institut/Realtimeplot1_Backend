# Experiments, process variables and data <!-- omit in toc -->

## Table of Content <!-- omit in toc -->
- [Database models](#database-models)
  - [ProcessVariable](#processvariable)
  - [Experiment](#experiment)
  - [User](#user)
- [Endpoints](#endpoints)
  - [Get a list of experiments](Get-a-list-of-all-process-variables)
    - [Response 200 OK](#response-200-ok)
  - [Get experiment data](#get-experiment-data)
    - [Response 200 OK](#response-200-ok-1)
    - [Response 404 NOT_FOUND - User in experiment not found](#response-404-NOT_FOUND---user-in-experiment-not-found)


## Database models

### ProcessVariable

| Column name         | type                              | primary key | unique | nullable | default value |
|---------------------|-----------------------------------|-------------|--------|----------|---------------|
| pv_string           | String(100)                       | True        | True   | False    | ---           |
| human_readable_name | String(100)                       | False       | False  | True     | ---           |
| experiment_short_id | ForeignKey("experiment.short_id") | False       | False  | False    | ---           |

*The `short_id` is automatically taken from the `pv_string`. It consists of all the characters before the first `:`.*

### Experiment

| Column name         | type                            | primary key | unique | nullable | default value |
|---------------------|---------------------------------|-------------|--------|----------|---------------|
| short_id            | db.String(100)                  | True        | True   | False    | ---           |
| human_readable_name | db.String(100)                  | False       | False  | True     | ---           |
| process_variables   | relationship("ProcessVariable") | False       | False  | True     | ---           |
| users               | db.relationship("User")         | False       | False  | True     | ---           |

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

*In the database there is a table users_to_experiments, which handles the relationship between users and experiments.*

## Endpoints

### Get a list of experiments

- Endpoint: `experiments/data`
- Method: `POST`

*Send an **admin** access token in the "x-access-tokens" header!*

#### Response 200 OK
```JSON
{
    "data": {
        "experiment": {
            "human_readable_name": null,
            "process_variable_urls": [
                "/experiments/pvs/Test:Machine3:FanSpeed1"
            ],
            "short_id": "Test"
        },
        "process_variables_data": {
            "Test:Machine3:FanSpeed1": [
                {
                    "data": 0.0,
                    "time": "2022-01-15 13:37:34.793888256+01:00"
                }
            ]
        }
    },
    "warnings": [
        "Time frame not specified. The data is in a server-defined time frame of 7 hours up to the current time."
    ]
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!


#### Response 404 NOT_FOUND - User in experiment not found
```JSON
{
    "errors": [
        "Only users that are assigned to the experiment can access it."
    ]
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!


### Get experiment data

- Endpoint: `/validate_pv_string/<pv_string>`
- Method: `GET`

*Send an **admin** access token in the "x-access-tokens" header!*

#### RESPONSE 200 OK
```JSON
{
    "experiment": {
        "human_readable_name": "...",
        "process_variable_urls": [
            "/experiments/pvs/...:...:...",
            "/experiments/pvs/...:...:...",
            "/experiments/pvs/...:...:...",
            "/experiments/pvs/...:...:...",
            "/experiments/pvs/...:...:..."
        ],
        "short_id": "...",
        "user_urls": [
            "/auth/users/..."
        ]
    }
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!


