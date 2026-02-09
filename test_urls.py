from pdf_rag.crawler.crawler import normalize_url, looks_like_pdf_url


def test_normalize_url_strips_fragment_and_trailing_slash():
    assert normalize_url("https://Example.com/path/#section") == "https://example.com/path"
    assert normalize_url("https://example.com/") == "https://example.com/"


def test_pdf_detection():
    assert looks_like_pdf_url("https://example.com/report.pdf")
    assert looks_like_pdf_url("https://example.com/download?file=report.pdf")
    assert not looks_like_pdf_url("https://example.com/about")
