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

## Endpoints

### Get a list of experiments

Send an access token in the "x-access-tokens" header that is related to a user in the experiment!*

- Endpoint: `experiments/data`
- Method: `POST`

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


