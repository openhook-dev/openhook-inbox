# Glama validation preparation

Prepared and locally checked on 2026-10-16 against source
`f77f16c72b2d022c2746b6af509d4f8484ad17dd`.

The [pending collection PR](https://github.com/punkpeye/awesome-mcp-servers/pull/16343)
requires a real Glama listing, passing checks and a resolving score badge. Local
validation does not satisfy those platform requirements.

## Container setup

Use the repository's root Dockerfile as the basis for Glama's Dockerfile editor.
Keep its locked dependencies, explicit source copies and non-root user. In the
final `core` stage, replace the HTTP command with:

```dockerfile
HEALTHCHECK NONE
CMD ["/app/.venv/bin/openhook"]
```

This uses the existing stdio entry point and disables the inherited HTTP health
check, which does not apply to stdio. These are validator-specific changes; the
production Dockerfile continues to serve HTTP. Build the `core` target, not the
`hosted` target. No billing credentials or provider keys are needed to initialize
and list the tools.

A temporary copy with those two changes built successfully. The MCP SDK then
initialized the container using `docker run --rm -i --network none`, discovered
29 tools and 3 resources, and exited cleanly. Image inspection confirmed user
`openhook`, the stdio command and disabled health check. No tools were invoked,
credentials supplied, or external callbacks sent during this check.

Stdio discovery does not start the public HTTP/email/DNS capture listeners. A
working self-hosted capture service needs the documented HTTP deployment and
network configuration; the hosted endpoint is `https://openhook.dev/mcp`.

## Remaining publication steps

1. Complete the Glama account sign-in. On 2026-10-16, Add Server opened its
   sign-up/sign-in dialog with account terms and a CAPTCHA; no account was created.
2. Submit the public source repository and the validator Dockerfile through
   Glama's interface. Inspect the platform's actual build and introspection results.
3. Verify the public listing and its actual score badge URL. Only then add that
   badge to the collection PR and mark the draft ready for curator review.

Glama's directory search returned a site error during this check, so it did not
establish whether an automatically imported Openhook listing exists. Recheck
before submitting to avoid a duplicate. Do not invent a badge or report local
success as a Glama certification.
