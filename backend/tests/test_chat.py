def test_chat_answer_returns_citation(client, auth_headers, sample_pdf_bytes):
    upload = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"files": ("policy.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200

    session = client.post("/api/v1/chat/sessions", headers=auth_headers, json={"title": "HR questions"})
    assert session.status_code == 200
    session_id = session.json()["id"]

    answer = client.post(
        f"/api/v1/chat/sessions/{session_id}/ask",
        headers=auth_headers,
        json={"question": "How many annual leave days do employees receive?"},
    )
    assert answer.status_code == 200
    payload = answer.json()
    assert "uploaded documents" in payload["answer"] or "12 days" in payload["answer"]
    assert payload["citations"]
    assert payload["citations"][0]["page_number"] == 1
