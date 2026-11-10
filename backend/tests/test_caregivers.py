def _register_login(client, email, name):
    client.post(
        "/users/register",
        json={"email": email, "password": "Passw0rd", "name": name},
    )
    token = client.post(
        "/login", data={"username": email, "password": "Passw0rd"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _me_id(client, headers):
    return client.get("/me", headers=headers).json()["id"]


def _setup(client):
    patient = _register_login(client, "patient@example.com", "Patient")
    caregiver = _register_login(client, "cg@example.com", "Caregiver")
    client.post(
        "/medications/", json={"name": "Aspirin", "dosage": "100mg"}, headers=patient
    )
    return patient, caregiver, _me_id(client, patient), _me_id(client, caregiver)


# --- invite links ----------------------------------------------------------

def _make_link(client, patient):
    resp = client.post("/caregivers/invite-links", headers=patient)
    assert resp.status_code == 200
    return resp.json()["token"]


def test_invite_link_flow_grants_access_only_after_accept(client):
    patient, caregiver, patient_id, _ = _setup(client)
    token = _make_link(client, patient)

    # Previewing shows who is asking but grants nothing.
    preview = client.get(f"/caregivers/invite-links/{token}", headers=caregiver)
    assert preview.status_code == 200
    assert preview.json()["patient_email"] == "patient@example.com"
    assert client.get(f"/caregivers/patients/{patient_id}/medications", headers=caregiver).status_code == 403

    resp = client.post(f"/caregivers/invite-links/{token}/accept", headers=caregiver)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACCEPTED"
    assert client.get(f"/caregivers/patients/{patient_id}/medications", headers=caregiver).status_code == 200
    assert client.get("/caregivers/me", headers=patient).json()[0]["status"] == "ACCEPTED"


def test_invite_link_is_single_use(client):
    patient, caregiver, _, _ = _setup(client)
    other = _register_login(client, "other@example.com", "Other")
    token = _make_link(client, patient)

    assert client.post(f"/caregivers/invite-links/{token}/accept", headers=caregiver).status_code == 200
    assert client.post(f"/caregivers/invite-links/{token}/accept", headers=other).status_code == 410
    assert client.get(f"/caregivers/invite-links/{token}", headers=other).status_code == 410


def test_invite_link_expires(client):
    from datetime import datetime, timedelta, timezone
    from conftest import TestingSessionLocal
    import database_utilis_related.models as models

    patient, caregiver, patient_id, _ = _setup(client)
    token = _make_link(client, patient)

    db = TestingSessionLocal()
    db.query(models.CaregiverInvite).update(
        {"expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)}
    )
    db.commit()
    db.close()

    assert client.post(f"/caregivers/invite-links/{token}/accept", headers=caregiver).status_code == 410
    assert client.get(f"/caregivers/patients/{patient_id}/medications", headers=caregiver).status_code == 403


def test_invite_link_rejects_bad_token_self_accept_and_anonymous(client):
    patient, caregiver, _, _ = _setup(client)
    token = _make_link(client, patient)

    assert client.get("/caregivers/invite-links/not-a-real-token", headers=caregiver).status_code == 404
    assert client.post(f"/caregivers/invite-links/{token}/accept", headers=patient).status_code == 400
    assert client.get(f"/caregivers/invite-links/{token}").status_code == 401
    assert client.post(f"/caregivers/invite-links/{token}/accept").status_code == 401
    assert client.post("/caregivers/invite-links").status_code == 401


def test_invite_token_is_not_stored_in_plain_text(client):
    from conftest import TestingSessionLocal
    import database_utilis_related.models as models

    patient, _, _, _ = _setup(client)
    token = _make_link(client, patient)

    db = TestingSessionLocal()
    stored = db.query(models.CaregiverInvite).one().token_hash
    db.close()
    assert stored != token and token not in stored


def test_patient_can_remove_caregiver_and_access_ends(client):
    patient, caregiver, patient_id, cg_id = _setup(client)
    token = _make_link(client, patient)
    client.post(f"/caregivers/invite-links/{token}/accept", headers=caregiver)
    assert client.get(f"/caregivers/patients/{patient_id}/medications", headers=caregiver).status_code == 200

    assert client.delete(f"/caregivers/{cg_id}", headers=patient).status_code == 200
    assert client.get("/caregivers/me", headers=patient).json() == []
    assert client.get(f"/caregivers/patients/{patient_id}/medications", headers=caregiver).status_code == 403
    assert client.get("/caregivers/me/patients", headers=caregiver).json() == []


def test_removed_caregiver_can_be_invited_again_with_a_new_link(client):
    patient, caregiver, patient_id, cg_id = _setup(client)
    client.post(f"/caregivers/invite-links/{_make_link(client, patient)}/accept", headers=caregiver)
    client.delete(f"/caregivers/{cg_id}", headers=patient)

    again = _make_link(client, patient)
    assert client.post(f"/caregivers/invite-links/{again}/accept", headers=caregiver).status_code == 200


def test_already_a_caregiver_cannot_accept_a_second_link(client):
    patient, caregiver, _, _ = _setup(client)
    client.post(f"/caregivers/invite-links/{_make_link(client, patient)}/accept", headers=caregiver)
    second = _make_link(client, patient)
    assert client.post(f"/caregivers/invite-links/{second}/accept", headers=caregiver).status_code == 400


def _legacy_pending_link(patient_id, cg_id):
    """A caregiver row from before invite links existed: never consented, so PENDING."""
    from conftest import TestingSessionLocal
    import database_utilis_related.models as models
    db = TestingSessionLocal()
    db.add(models.CareGiver(user_id=patient_id, cg_id=cg_id, status=models.CaregiverStatus.PENDING))
    db.commit()
    db.close()


def test_legacy_pending_row_grants_nothing_and_patient_can_remove_it(client):
    patient, caregiver, patient_id, cg_id = _setup(client)
    _legacy_pending_link(patient_id, cg_id)

    assert client.get(f"/caregivers/patients/{patient_id}/medications", headers=caregiver).status_code == 403
    assert client.get("/caregivers/me/patients", headers=caregiver).json() == []
    assert client.get("/caregivers/me", headers=patient).json()[0]["status"] == "PENDING"
    assert client.delete(f"/caregivers/{cg_id}", headers=patient).status_code == 200


def test_accepting_a_link_activates_a_legacy_pending_row_without_duplicating(client):
    patient, caregiver, patient_id, cg_id = _setup(client)
    _legacy_pending_link(patient_id, cg_id)

    token = _make_link(client, patient)
    assert client.post(f"/caregivers/invite-links/{token}/accept", headers=caregiver).status_code == 200
    assert len(client.get("/caregivers/me", headers=patient).json()) == 1
    assert client.get(f"/caregivers/patients/{patient_id}/medications", headers=caregiver).status_code == 200


def test_by_user_id_invitation_endpoints_are_gone(client):
    patient, caregiver, patient_id, cg_id = _setup(client)
    body = {"user_id": patient_id, "cg_id": cg_id}
    assert client.post("/caregivers/assign", json=body, headers=patient).status_code in (404, 405)
    assert client.get("/caregivers/invitations", headers=caregiver).status_code in (404, 405)
    assert client.post("/caregivers/invitations/1/accept", headers=caregiver).status_code in (404, 405)
    assert client.delete("/caregivers/invitations/1", headers=caregiver).status_code in (404, 405)
