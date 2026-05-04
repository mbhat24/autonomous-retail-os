from urllib.parse import urlencode


def build_upi_uri(
    *,
    payee_vpa: str,
    payee_name: str,
    amount: float,
    transaction_note: str,
    transaction_ref: str,
    currency: str = "INR",
) -> str:
    params = {
        "pa": payee_vpa,
        "pn": payee_name,
        "am": f"{amount:.2f}",
        "cu": currency,
        "tn": transaction_note,
        "tr": transaction_ref,
    }
    return f"upi://pay?{urlencode(params)}"
