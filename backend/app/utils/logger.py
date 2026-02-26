from datetime import datetime


def log_transaction_event(message: str):
    timestamp = datetime.utcnow().isoformat()
    with open("transaction.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")
