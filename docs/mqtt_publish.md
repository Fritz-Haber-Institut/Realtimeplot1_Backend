# Setting variables via MQTT Publish <!-- omit in toc -->

## Table of Content <!-- omit in toc -->
- [Endpoints](#endpoints)
  - [Set new values for prozess variables](#set-new-values-for-prozess-variables)
    - [Response 400 BAD REQUEST - "value" not specified](#response-400-bad-request---value-not-specified)
    - [Response 403 FORBIDDEN - User not assigned to the experiment](#response-403-forbidden---user-not-assigned-to-the-experiment)
    - [RESPONSE 406 NOT ACCEPTABLE - process variable does not accept user-set values](#response-406-not-acceptable---process-variable-does-not-accept-user-set-values)
    - [RESPONSE 200 OK](#response-200-ok)

## Endpoints

### Set new values for process variables

- Endpoint: `publish/<pv_string>`
- Method: `PUT`

```JSON
{
    "value": "..."
}
```

#### Response 400 BAD REQUEST - "value" not specified
```JSON
{
    "errors": ["The value to be set must be supplied in the JSON body."]
}
```

#### Response 403 FORBIDDEN - User not assigned to the experiment
```JSON
{
    "errors": [
        "Process variable data can only be overwritten by users assigned to the associated experiment."
    ]
}
```

#### RESPONSE 406 NOT ACCEPTABLE - process variable does not accept user-set values
```JSON
{
    "errors": [
        "The requested process variable does not accept user-set values."
    ]
}
```

#### RESPONSE 200 OK
```JSON
{
    "messages": [
        "Your request has been sent to the MQTT server. It may take a while for the changes to take effect."
    ]
}
```

***Caution!** The 200 OK answer is no guarantee for a successful setting of the variable. It only confirms that the Server successfully sent a request to the MQTT server.*

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

Also check out: [Responses for requests with JSON bodies](cross_endpoint_responses.md#responses-for-requests-with-json-bodies)!

Also check out: [Responses for requests which try to query resources that do not exist in the database](cross_endpoint_responses.md#responses-for-requests-which-try-to-query-resources-that-do-not-exist-in-the-database)!

Also check out: [Responses to requests that result in server-side communication with another MQTT server](cross_endpoint_responses.md#responses-to-requests-that-result-in-server-side-communication-with-another-mqtt-server)!
