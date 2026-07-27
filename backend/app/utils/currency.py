def format_zwl(amount: float) -> str:
    return f"ZiG {amount:,.2f}"


def format_usd(amount: float) -> str:
    return f"USD {amount:,.2f}"


def format_currency(amount: float, currency: str = "USD") -> str:
    if currency.upper() in ("ZIG", "ZWL", "RTGS"):
        return format_zwl(amount)
    return format_usd(amount)
