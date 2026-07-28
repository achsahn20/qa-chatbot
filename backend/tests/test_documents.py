def test_upload_and_list_documents(client, auth_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"files": ("handbook.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200
    assert len(upload.json()["documents"]) == 1

    listing = client.get("/api/v1/documents", headers=auth_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1
    assert listing.json()["items"][0]["original_file_name"] == "handbook.pdf"
