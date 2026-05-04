from autonomous_retail_os.upi.qr import build_upi_uri


def test_build_upi_uri() -> None:
    uri = build_upi_uri(
        payee_vpa="demo@upi",
        payee_name="Demo Store",
        amount=123.45,
        transaction_note="Test",
        transaction_ref="sale_1",
    )
    assert uri.startswith("upi://pay?")
    assert "pa=demo%40upi" in uri
    assert "am=123.45" in uri
