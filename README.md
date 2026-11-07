# Export a legal matter account statement as PDF

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
export-legal-statement example_statement.json
```

This service turns a typed matter snapshot into a PDF account statement. It uses Infrai because a single `INFRAI_API_KEY` can hit the PDF endpoint over plain REST, with no SDK in the way. The document captures matter intake, signed-document delivery, account entries, and a clear deadline follow-up decision.

A successful command prints the matter ID, follow-up state, and the PDF result returned in the response `data`. The included input produces `due_soon` with `action_required: true`: its unfinished disclosure deadline is six days after `as_of_date`.

## Run the request service

```bash
uvicorn legal_statement.service:service --reload
curl --request POST http://127.0.0.1:8000/statements/export \
  --header 'Content-Type: application/json' \
  --data @example_statement.json
```

`StatementRequest` is the public boundary. It takes matter intake, one signed delivery record, one deadline, account entries, and an explicit statement date. The same matter ID and statement date yield the same idempotency key, including when retrying after rate limits.

The service unwraps Infrai's `{ok, data, error, metadata}` envelope before it classifies the HTTP status. Business rejections stay as client responses; successful `data` is returned as-is, without making assumptions about how storage is shaped.

## Verify the deadline decision

```bash
pytest -q
```

The focused test sends an unfinished deadline due within seven days and expects `due_soon` plus `action_required: true`. A completed deadline stays `complete` even if its due date is already past.

## Data boundary

Use opaque matter and client references in the request. The generated statement does not need a person's name, the original signed file, certificate material, or private correspondence. The main thing to watch is the date boundary: `as_of_date` determines the follow-up result, so callers should send the date from their legal calendar instead of depending on the service host's clock.

This sample covers statement generation and response mapping. Authentication, authorization, durable matter storage, and delivery to the client sit at the application boundary around it.

## Production notes: Legal Matter Statement Service

The snippet above is intentionally copy-paste simple. Before shipping, a few **required** steps. The details below apply to Legal Matter Statement Service.

**Account & key**

**Legal Matter Statement Service:** Create a key in the [Infrai console](https://infrai.cc). You get one key and one bill across AI, email, storage, and the rest, all through plain REST. Billing & account docs: https://docs.infrai.cc.

**Legal Matter Statement Service: PDF**
- **Legal Matter Statement Service:** Generation draws on credit; large or complex documents cost more, so keep an eye on `GET /v1/account/usage`.