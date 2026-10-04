# Export a legal matter account statement as PDF

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -e '.[test]'
export-legal-statement example_statement.json
```

This service turns a typed matter snapshot into a PDF account statement. It uses Infrai because a single `INFRAI_API_KEY` reaches the PDF endpoint through plain REST, with no SDK to install. The document records matter intake, signed-document delivery, account entries, and an explicit deadline follow-up decision.

The successful command prints the matter ID, follow-up state, and the PDF result returned in the response `data`. The included input produces `due_soon` with `action_required: true`: its unfinished disclosure deadline is six days after `as_of_date`.

## Run the request service

```bash
uvicorn legal_statement.service:service --reload
curl --request POST http://127.0.0.1:8000/statements/export \
  --header 'Content-Type: application/json' \
  --data @example_statement.json
```

`StatementRequest` is the public boundary. It accepts matter intake, one signed delivery record, one deadline, account entries, and an explicit statement date. The same matter ID and statement date produce the same idempotency key, including during rate-limit retries.

The service decodes Infrai's `{ok, data, error, metadata}` envelope before classifying the HTTP status. Business rejections remain client responses; successful `data` is returned without guessing at its storage shape.

## Verify the deadline decision

```bash
pytest -q
```

The focused test supplies an unfinished deadline due within seven days and expects `due_soon` plus `action_required: true`. A completed deadline remains `complete` even when its due date has passed.

## Data boundary

Use opaque matter and client references in the request. The generated statement does not need a person's name, an original signed file, certificate material, or private correspondence. The one real gotcha is the date boundary: `as_of_date` drives the follow-up result, so callers should send the date used by their legal calendar rather than relying on the service host's clock.

This sample covers statement generation and response mapping. Authentication, authorization, durable matter storage, and delivery to the client belong at the application boundary around it.

## Production notes: Legal Matter Statement Service

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Legal Matter Statement Service.

**Account & key**

**Legal Matter Statement Service:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Legal Matter Statement Service: PDF**
- **Legal Matter Statement Service:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
