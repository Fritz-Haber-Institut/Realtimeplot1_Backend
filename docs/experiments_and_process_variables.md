# Experiments and Process variables <!-- omit in toc -->

## Table of Content <!-- omit in toc -->
- [Database models](#database-models)
  - [ProcessVariable](#processvariable)
  - [Experiment](#experiment)
- [Endpoints](#endpoints)
  - [Get a list of all process variables](#get-a-list-of-all-process-variables)
    - [Response 200 OK](#response-200-ok)
  - [Create a process variable](#create-a-process-variable)
    - [Response 200 OK](#response-200-ok-1)
    - [Response 400 BAD REQUEST - Missing `pv_string`](#response-400-bad-request---missing-pv_string)
  - [Get process variable data](#get-process-variable-data)
    - [Response 200 OK](#response-200-ok-2)
  - [Change process variable data](#change-process-variable-data)
    - [Response 200 OK](#response-200-ok-3)
  - [Delete process variable](#delete-process-variable)
  - [Get a list of all experiments](#get-a-list-of-all-experiments)
    - [Response 200 OK](#response-200-ok-4)
  - [Create an experiment](#create-an-experiment)
  - [Get experiment data](#get-experiment-data)
    - [RESPONSE 200 OK](#response-200-ok-5)
  - [Change an experiment](#change-an-experiment)
    - [Response 200 OK](#response-200-ok-6)
  - [Delete an experiment](#delete-an-experiment)

## Database models

### ProcessVariable

| Column name           | type                                 | primary key | unique | nullable | default value |
|-----------------------|--------------------------------------|-------------|--------|----------|---------------|
| pv_string             | String(100)                          | True        | True   | False    | ---           |
| human_readable_name   | String(100)                          | False       | False  | True     | ---           |
| experiment_short_id   | ForeignKey("experiment.short_id")    | False       | False  | False    | ---           |
| default_threshold_min | db.Column(db.Integer)                | False       | False  | True     | ---           |
| default_threshold_max | db.Column(db.Integer)                | False       | False  | True     | ---           |

*The `short_id` is automatically taken from the `pv_string`. It consists of all the characters before the first `:`.*

### Experiment

| Column name                | type                            | primary key | unique | nullable | default value |
|----------------------------|---------------------------------|-------------|--------|----------|---------------|
| short_id                   | db.String(100)                  | True        | True   | False    | ---           |
| human_readable_name        | db.String(100)                  | False       | False  | True     | ---           |
| process_variables          | relationship("ProcessVariable") | False       | False  | True     | ---           |
| users                      | db.relationship("User")         | False       | False  | True     | ---           |
| available_for_mqtt_publish | db.Column(db.Boolean)           | False       | False  | False    | False         |

*In the database there is a table users_to_experiments, which handles the relationship between users and experiments.*

## Endpoints

### Get a list of all process variables

- Endpoint: `experiments/pvs`
- Method: `GET`

*Send an **admin** access token in the "x-access-tokens" header!*

#### Response 200 OK
```JSON
{
    "process_variables": [
        {
            "experiment_short_id": "...",
            "human_readable_name": null,
            "pv_string": "...:...:...",
            "default_threshold_min": ...,  # int
            "default_threshold_max": ... # int
        },
        {
            "experiment_short_id": "...",
            "human_readable_name": "...",
            "pv_string": "...:...:...",
            "default_threshold_min": null,
            "default_threshold_max": null
        },
        {
            "experiment_short_id": "...",
            "human_readable_name": null,
            "pv_string": "...:...:...",
            "default_threshold_min": ...,  # int
            "default_threshold_max": null
        }
    ]
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

### Create a process variable

- Endpoint: `experiments/pvs`
- Method: `POST`

*Send an **admin** access token in the "x-access-tokens" header!*

```JSON
{
    "pv_string": "Test:Machine3:FanSpeed1",
    "human_readable_name": "Machine 03"
}
```

*The `human_readable_name` key is optional.*

#### Response 200 OK
```JSON
{
    "process_variable": {
        "experiment_short_id": "Test",
        "human_readable_name": "Machine 03",
        "pv_string": "Test:Machine3:FanSpeed1",
        "default_threshold_min": 20,
        "default_threshold_max": 80
    }
}
```

*The `experiment_short_id` is taken from the `pv_string`. If there is no experiment with this `short_id`, one will be created automatically.*

#### Response 400 BAD REQUEST - Missing `pv_string`
```JSON
{
    "errors": [
        {
            "pv_string": "No pv_string was specified. To create a process variable, you must provide a pv_string because it serves as primary_key."
        }
    ]
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests that try to add already existing objects to the database](cross_endpoint_responses.md#responses-for-requests-that-try-to-add-already-existing-objects-to-the-database)!

### Get process variable data

- Endpoint: `experiments/pvs/<pv_string>`
- Method: `GET`

*Send an **admin** access token in the "x-access-tokens" header!*

#### Response 200 OK
```JSON
{
    "process_variable": {
        "experiment_short_id": "...",
        "human_readable_name": null,
        "pv_string": "...:...:...",
        "default_threshold_min": ...,  # int
        "default_threshold_max": null
    }
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

### Change process variable data

- Endpoint: `experiments/pvs/<pv_string>`
- Method: `PUT`

*Send an **admin** access token in the "x-access-tokens" header!*

```JSON
{
    "pv_string": "ABC:Machine1:FanSpeed1",
    "human_readable_name": "Experiment ABC - Machine 1 - FanSpeed 1",
    "experiment_short_id": "DEF",
    "default_threshold_min": 20,
    "default_threshold_max": 80
}
```

#### Response 200 OK
```JSON
{
    "errors": [
        "experiment_short_id: The experiment_short_id cannot be changed manually as it is generated from the pv_string. Change the characters in the pv_string before the first colon to change the short_id and thus assign the pv_string to a new experiment."
    ],
    "process_variable": {
        "experiment_short_id": "ABC",
        "human_readable_name": "Experiment ABC - Machine 1 - FanSpeed 1",
        "pv_string": "ABC:Machine1:FanSpeed1",
        "default_threshold_min": 20,
        "default_threshold_max": 80
    }
}
```

*An attempt to change the `short_id` is ignored and triggers an error message. Valid changes to the `pv_string` or the `human_readable_name` are still made.*

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

### Delete process variable

- Endpoint: `experiments/pvs/<pv_string>`
- Method: `DELETE`

*Send an **admin** access token in the "x-access-tokens" header!*

*Deleting the last/only process variable in an experiment also deletes the experiment. Add more process variables first if you want the experiment to persist!*

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

Also check out: [Responses for requests which delete database objects](cross_endpoint_responses.md#responses-for-requests-which-delete-database-objects)!

### Get a list of all experiments

- Endpoint: `experiments`
- Method: `GET`

*Send an **admin** access token in the "x-access-tokens" header!*

#### Response 200 OK
```JSON
{
    "experiments": [
        {
            "human_readable_name": "...",
            "process_variable_urls": [
                "/experiments/pvs/...:...:...",
                "/experiments/pvs/...:...:...",
                "/experiments/pvs/...:...:...",
            ],
            "short_id": "...",
            "user_urls": [
                "/auth/users/..."
            ]
        },
        {
            "human_readable_name": null,
            "process_variable_urls": [
                "/experiments/pvs/...:...:...",
                "/experiments/pvs/...:...:..."
            ],
            "short_id": "...",
            "user_urls": []
        }
    ]
}
```

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

### Create an experiment

***Empty experiments without process variables are not supported. Therefore, you cannot create experiments manually. Create process variables via [the intended endpoint](#create-a-process-variable). Experiments are then automatically generated using the `experiment_short_id` in the `pv_strings`.***

### Get experiment data

- Endpoint: `experiments/<experiment_short_id>`
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

### Change an experiment

- Endpoint: `experiments/<experiment_short_id>`
- Method: `PUT`

*Send an **admin** access token in the "x-access-tokens" header!*

```JSON
{
    "human_readable_name": "...",
    "users_to_add": ["..."],
    "users_to_remove": ["...", "..."]
}
```

*To assign users to an experiment, send their `user_id`s in a list using the `users_to_add` key.*

*To remove users from an experiment, send their `user_id`s in a list using the `users_to_remove` key.*

*The `short_id` cannot be changed. An attempt leads to the message in `errors`: `"short_id: The short_id cannot be changed at the moment. Edit the individual process variables to create a new experiment with a new short_id!"`, which **does not lead to termination**. All valid changes will still be made.*

*If an attempt is made to add a user whose `user_id` does not exist, the following message is output in `errors`: `"users_to_add: The user (...) does not exist and therefore cannot be added to the experiment."`. This **does not lead to termination**. The user_id is simply **ignored** and the client is informed via the error message.*

#### Response 200 OK
```JSON
{
    "errors": [],
    "experiment": {
        "human_readable_name": "...",
        "process_variable_urls": [
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

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

### Delete an experiment

- Endpoint: `experiments/<experiment_short_id>`
- Method: `DELETE`

*Deleting an experiment also triggers **the deletion of all of its process variables**.*

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

Also check out: [Responses for requests which delete database objects](cross_endpoint_responses.md#responses-for-requests-which-delete-database-objects)!
