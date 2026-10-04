# Openhook tool reference

26 native tools. Generated with `uv run python scripts/generate_docs.py`.

Keep private management tokens and provider credentials out of shared documents.

## check_for_callbacks

Check for callbacks newer than a sequence cursor without waiting.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "since": {
      "default": 0,
      "title": "Since",
      "type": "integer"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "check_for_callbacksArguments",
  "type": "object"
}
```

## configure_webhook

Set HTTP responses and optional SHA256 HMAC verification, preserving unspecified fields.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "default_status": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Default Status"
    },
    "default_content": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "items": {},
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Default Content"
    },
    "default_content_type": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Default Content Type"
    },
    "cors": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Cors"
    },
    "verification_secret": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Verification Secret"
    },
    "signature_provider": {
      "anyOf": [
        {
          "enum": [
            "generic",
            "github",
            "stripe",
            "linear"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Signature Provider"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "configure_webhookArguments",
  "type": "object"
}
```

## create_webhook

Create an inbox. Save its private token; share only its public capture addresses.

```json
{
  "properties": {
    "expiry": {
      "default": 604800,
      "title": "Expiry",
      "type": "integer"
    },
    "name": {
      "default": "",
      "title": "Name",
      "type": "string"
    }
  },
  "title": "create_webhookArguments",
  "type": "object"
}
```

## delete_all_requests

Clear stored events, keeping the inbox's addresses and settings.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "delete_all_requestsArguments",
  "type": "object"
}
```

## delete_request

Permanently delete one event belonging to this inbox.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "request_id": {
      "title": "Request Id",
      "type": "string"
    }
  },
  "required": [
    "webhook_token",
    "request_id"
  ],
  "title": "delete_requestArguments",
  "type": "object"
}
```

## delete_webhook

Permanently delete this inbox and its stored events.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "delete_webhookArguments",
  "type": "object"
}
```

## download_request_file

Retrieve exact captured bytes as base64, including binary bodies or raw MIME.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "request_id": {
      "title": "Request Id",
      "type": "string"
    }
  },
  "required": [
    "webhook_token",
    "request_id"
  ],
  "title": "download_request_fileArguments",
  "type": "object"
}
```

## export_webhook_data

Export a bounded page of full events; resume with next_since. Browser export streams the entire inbox.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "format": {
      "default": "json",
      "enum": [
        "json",
        "csv"
      ],
      "title": "Format",
      "type": "string"
    },
    "since": {
      "default": 0,
      "title": "Since",
      "type": "integer"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "export_webhook_dataArguments",
  "type": "object"
}
```

## extract_links_from_request

Extract HTTP links and verification codes without visiting the URLs.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "request_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Request Id"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "extract_links_from_requestArguments",
  "type": "object"
}
```

## generate_oob_payloads

Read callback addresses for authorized out-of-band testing.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "generate_oob_payloadsArguments",
  "type": "object"
}
```

## get_request

Read a complete event; omit request_id to inspect the newest one.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "request_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Request Id"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "get_requestArguments",
  "type": "object"
}
```

## get_webhook_email

Read the email address, available when this deployment runs SMTP.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "get_webhook_emailArguments",
  "type": "object"
}
```

## get_webhook_info

Read addresses, expiry, response settings, and retained event count.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "get_webhook_infoArguments",
  "type": "object"
}
```

## get_webhook_requests

Read events with pagination or a durable sequence cursor.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "limit": {
      "default": 50,
      "title": "Limit",
      "type": "integer"
    },
    "page": {
      "default": 1,
      "title": "Page",
      "type": "integer"
    },
    "since": {
      "default": 0,
      "title": "Since",
      "type": "integer"
    },
    "request_type": {
      "anyOf": [
        {
          "enum": [
            "web",
            "email",
            "dns"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Request Type"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "get_webhook_requestsArguments",
  "type": "object"
}
```

## register_github_webhook

Create a signed GitHub repository subscription and native inbox. Requires webhook-write permission.

```json
{
  "properties": {
    "access_token": {
      "title": "Access Token",
      "type": "string"
    },
    "repository": {
      "title": "Repository",
      "type": "string"
    },
    "events": {
      "items": {
        "type": "string"
      },
      "title": "Events",
      "type": "array"
    }
  },
  "required": [
    "access_token",
    "repository",
    "events"
  ],
  "title": "register_github_webhookArguments",
  "type": "object"
}
```

## register_linear_webhook

Create a signed Linear subscription and native inbox. Requires admin scope; optional team filter.

```json
{
  "properties": {
    "access_token": {
      "title": "Access Token",
      "type": "string"
    },
    "resource_types": {
      "items": {
        "type": "string"
      },
      "title": "Resource Types",
      "type": "array"
    },
    "team_id": {
      "default": "",
      "title": "Team Id",
      "type": "string"
    }
  },
  "required": [
    "access_token",
    "resource_types"
  ],
  "title": "register_linear_webhookArguments",
  "type": "object"
}
```

## register_stripe_webhook

Create a signed Stripe webhook endpoint and native inbox. Provider credentials are not stored.

```json
{
  "properties": {
    "access_token": {
      "title": "Access Token",
      "type": "string"
    },
    "events": {
      "items": {
        "type": "string"
      },
      "title": "Events",
      "type": "array"
    }
  },
  "required": [
    "access_token",
    "events"
  ],
  "title": "register_stripe_webhookArguments",
  "type": "object"
}
```

## respond_to_next_request

Respond to the next request using ?openhook_wait=1, within its 20-second response window.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "content": {
      "title": "Content",
      "type": "string"
    },
    "status": {
      "default": 200,
      "title": "Status",
      "type": "integer"
    },
    "content_type": {
      "default": "text/plain",
      "title": "Content Type",
      "type": "string"
    },
    "timeout_seconds": {
      "default": 60,
      "title": "Timeout Seconds",
      "type": "number"
    }
  },
  "required": [
    "webhook_token",
    "content"
  ],
  "title": "respond_to_next_requestArguments",
  "type": "object"
}
```

## rotate_webhook_token

Revoke the old private token and return a new one; capture addresses stay unchanged.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "rotate_webhook_tokenArguments",
  "type": "object"
}
```

## search_requests

Search captured bodies, URLs, and headers for a literal substring.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "query": {
      "title": "Query",
      "type": "string"
    },
    "request_type": {
      "anyOf": [
        {
          "enum": [
            "web",
            "email",
            "dns"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Request Type"
    },
    "limit": {
      "default": 50,
      "title": "Limit",
      "type": "integer"
    },
    "page": {
      "default": 1,
      "title": "Page",
      "type": "integer"
    }
  },
  "required": [
    "webhook_token",
    "query"
  ],
  "title": "search_requestsArguments",
  "type": "object"
}
```

## send_requests

Create up to ten marked test HTTP events in this inbox.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "payloads": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Payloads",
      "type": "array"
    }
  },
  "required": [
    "webhook_token",
    "payloads"
  ],
  "title": "send_requestsArguments",
  "type": "object"
}
```

## server_status

Inspect native storage, retention, and enabled capture transports.

```json
{
  "properties": {},
  "title": "server_statusArguments",
  "type": "object"
}
```

## unregister_webhook

Remove the registered provider subscription and permanently delete its native inbox and events.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "access_token": {
      "title": "Access Token",
      "type": "string"
    }
  },
  "required": [
    "webhook_token",
    "access_token"
  ],
  "title": "unregister_webhookArguments",
  "type": "object"
}
```

## update_request

Annotate an event without changing its original captured body.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "request_id": {
      "title": "Request Id",
      "type": "string"
    },
    "note": {
      "title": "Note",
      "type": "string"
    }
  },
  "required": [
    "webhook_token",
    "request_id",
    "note"
  ],
  "title": "update_requestArguments",
  "type": "object"
}
```

## wait_for_email

Wait for an email received by Openhook's SMTP listener.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "timeout_seconds": {
      "default": 60,
      "title": "Timeout Seconds",
      "type": "number"
    },
    "since": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Since"
    },
    "return_existing": {
      "default": false,
      "title": "Return Existing",
      "type": "boolean"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "wait_for_emailArguments",
  "type": "object"
}
```

## wait_for_request

Wait up to 120 seconds; pass next_since when reconnecting to avoid missing events.

```json
{
  "properties": {
    "webhook_token": {
      "title": "Webhook Token",
      "type": "string"
    },
    "timeout_seconds": {
      "default": 60,
      "title": "Timeout Seconds",
      "type": "number"
    },
    "request_type": {
      "anyOf": [
        {
          "enum": [
            "web",
            "email",
            "dns"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Request Type"
    },
    "since": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Since"
    },
    "return_existing": {
      "default": false,
      "title": "Return Existing",
      "type": "boolean"
    }
  },
  "required": [
    "webhook_token"
  ],
  "title": "wait_for_requestArguments",
  "type": "object"
}
```
