# Bot Integration Notes

The backend already exposes ready-to-connect webhook endpoints:
- `POST /v1/bots/whatsapp/webhook`
- `POST /v1/bots/telegram/webhook`

Expected payload:

```json
{
  "contact": "+919876543210",
  "text": "1",
  "channel": "whatsapp",
  "profile_name": "Raju"
}
```

What the backend already handles:
- new-shop onboarding over chat
- category capture and PIN capture
- optional UPI capture
- daily open/close commands
- service catalog listing
- payment link responses

What still belongs in the provider adapter:
- Meta or Telegram signature verification
- mapping provider payloads into the backend format
- sending the backend reply text back to the chat provider
