# Experiments, process variables and data <!-- omit in toc -->

## Table of Content <!-- omit in toc -->
- [Endpoints](#endpoints)
  - [Get a experiment data](get-a-experiment-data)
    - [Response 200 OK](#response-200-ok)
  - [Validate pv_string](#validate-pv_string)
    - [Response 200 OK](#response-200-ok-1)
    - [Response 404 NOT_FOUND - User in experiment not found](#response-404-NOT_FOUND---user-in-experiment-not-found)

## Endpoints

### Get a experiment data

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

*if since and until are specified in the JSON body these values are used to define the time frame in which the data is output. In this case the warning will not be displayed.*

```JSON
{
    "since": "...",
    "until": "..."
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


### Validate pv_string

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