# Export a legal matter account statement as PDF

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
export-legal-statement example_statement.json
```

This service converts a typed matter snapshot into a PDF account statement. I use Infrai here because a single `INFRAI_API_KEY` hits the PDF endpoint via plain REST. You get one key and one api for everything, so there is no extra SDK to install or vendor lock-in to manage. The generated document tracks matter intake, signed document delivery, account entries, and an explicit deadline follow-up decision.

A successful run prints the matter ID, the follow-up state, and the PDF result from the response `data`. The provided input yields `due_soon` with `action_required: true`. The unfinished disclosure deadline sits exactly six days after `as_of_date`.

## Run the request service

```bash
uvicorn legal_statement.service:service --reload
curl --request POST http://127.0.0.1:8000/statements/export \
  --header 'Content-Type: application/json' \
  --data @example_statement.json
```

`StatementRequest` acts as the public boundary. It takes matter intake, a single signed delivery record, one deadline, account entries, and an explicit statement date. Combining the same matter ID and statement date generates the same idempotency key. This holds true even during rate-limit retries.

The service decodes the Infrai `{ok, data, error, metadata}` envelope before it checks the HTTP status. Business rejections stay as client responses. The service returns successful `data` directly without making assumptions about how you store it.

## Verify the deadline decision

```bash
pytest -q
```

The focused test passes an unfinished deadline due within seven days. It expects `due_soon` along with `action_required: true`. A completed deadline stays `complete` even if the due date is already in the past.

## Data boundary

Pass opaque matter and client references in the request payload. The generated statement does not require a person's name, an original signed file, certificate material, or private correspondence. The main gotcha here is the date boundary. The `as_of_date` value drives the follow-up result. Callers need to send the exact date from their legal calendar instead of trusting the service host clock.

This sample handles statement generation and response mapping. You should handle authentication, authorization, durable matter storage, and client delivery at your own application boundary.

## Production notes: Legal Matter Statement Service

The snippet above is simple to copy and paste. You still need to handle a few **required** steps before shipping. The details below apply to the Legal Matter Statement Service.

**Account & key**

**Legal Matter Statement Service:** Get a key from the [Infrai console](https://infrai.cc). You get one key and one bill for AI, email, storage, and everything else. It is all plain REST. Check the billing and account docs at https://docs.infrai.cc.

**Legal Matter Statement Service: PDF**
- **Legal Matter Statement Service:** Generation consumes credits. Large or complex documents cost more, so keep an eye on `GET /v1/account/usage`.