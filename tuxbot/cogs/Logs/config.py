from structured_config import Structure, StrField

HAS_MODELS = False


class LogsConfig(Structure):
    dm: str = StrField("")
    mentions: str = StrField("")
    guilds: str = StrField("")
    errors: str = StrField("")
    gateway: str = StrField("")
    sentryKey: str = StrField("")


extra = {
    "dm": {
        "type": str,
        "description": "URL of the webhook used for send DMs "
        "received and sent by the bot",
    },
    "mentions": {
        "type": str,
        "description": "URL of the webhook used for send Mentions "
        "received by the bot",
    },
    "guilds": {
        "type": str,
        "description": "URL of the webhook used for send guilds where the "
        "bot is added or removed",
    },
    "errors": {
        "type": str,
        "description": "URL of the webhook used for send errors in the bot",
    },
    "gateway": {
        "type": str,
        "description": "URL of the webhook used for send gateway information",
    },
    "sentryKey": {
        "type": str,
        "description": "Sentry KEY for error logging (https://sentry.io/)",
    },
}
