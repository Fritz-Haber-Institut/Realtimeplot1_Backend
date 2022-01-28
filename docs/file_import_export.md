# Import and export of experiment configurations <!-- omit in toc -->

Administrators can export the database entries for experiments and process variables to a file and import them on a new server instance.

## Table of contents  <!-- omit in toc -->
- [File structure](#file-structure)
  - [Experiments:](#experiments)
  - [Process variables](#process-variables)
- [Endpoints](#endpoints)
  - [Export to file](#export-to-file)
    - [Response 200 OK](#response-200-ok)
  - [Import from file](#import-from-file)
    - [Response 200 OK](#response-200-ok-1)

## File structure

- Leading or trailing spaces **are ignored**
- All lines that do not start with `[EXPERIMENT]` or `[PROCESS_VARIABLE]` after leading spaces **are ignored**
- Attributes of the entries are **separated by semicolons** (CSV)
- An `=` symbol separates the keys of the attributes and their values
- Unknown keys **are ignored**
- Bools are described as strings containing `True`, `False`, `true`, or `false`.
- Only attributes that should or must be set must be present

### Experiments:

- Example: `[EXPERIMENT];short_id=TEST;human_readable_name=TEST-Experiment`

### Process variables

- Example: `[PROCESS_VARIABLE];pv_string=TEST:Machine1:PowerOn;human_readable_name="Machine 1 - State";experiment_short_id=TESTavailable_for_mqtt_publish=False;default_threshold_min=20;default_threshold_max=50`

## Endpoints

### Export to file

- Endpoint: `file/export`
- Method: `POST`

*Send an **admin** access token in the "x-access-tokens" header!*

#### Response 200 OK

The following data is supplied to create the file:

- In the body: file content
- In the "Content-Type" header: type of content `"text/plain; charset=utf-8"`
- In the "Content-Disposition" header: `"attachment; filename=\<date>-\<time>-rtpserver-export.rtpdb"`


***Example file name:** 20220128-104610-rtpserver-export.rtpdb*

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

### Import from file

- Endpoint: `file/import`
- Method: `GET`

*Send an **admin** access token in the "x-access-tokens" header!*

*Send the content of the imported file as **text/plain** in the request body!*

#### Response 200 OK
```JSON
{
    "errors": [
        "line-...: An error occurred while creating the process variable. Check if the pv_string and the other attributes are set correctly, and start the import again. Valid process variables are not affected."
    ],
    "messages": [
        "Import complete. Please check the number of entries found, compare them with the number in the database, and consult the error messages if necessary!"
    ],
    "number_of_experiments_found_in_file": ...,  # int
    "number_of_experiments_now_in_database": ...,  # int
    "number_of_process_variables_found_in_file": ...,  # int
    "number_of_process_variables_now_in_database": ...,  # int
}
```

*If errors have occurred, the line in which the error happened is included in the error message. See "line-\<line>" in errors.*

Also check out: [Responses from endpoints that require an access token](cross_endpoint_responses.md#responses-from-endpoints-that-require-an-access-token)!

