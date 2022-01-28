# Get visualization data from experiments and process variables <!-- omit in toc -->

## Table of Content <!-- omit in toc -->
- [Endpoints](#endpoints)
  - [Get experiment data](#get-experiment-data)
    - [Response 200 OK](#response-200-ok)
  - [Validate pv_string](#validate-pv_string)
    - [RESPONSE 200 OK](#response-200-ok-1)

## Endpoints

### Get experiment data

Send an access token in the "x-access-tokens" header that is related to a user in the experiment!*

- Endpoint: `/data/<experiment_short_id>`
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

*If `since` and `until` are specified in the request JSON body, these values are used to define the time frame in which the data is output. In this case, the warning will not be displayed in the response.*

```JSON
{
    "since": "...",
    "until": "..."
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests that call endpoints that can only be called by users assigned to the queried experiments](cross_endpoint_responses.md#responses-for-requests-that-call-endpoints-that-can-only-be-called-by-users-assigned-to-the-queried-experiments)!

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
