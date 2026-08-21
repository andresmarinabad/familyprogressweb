import json
import pytest
import io
import os
import subprocess
import sys
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from PIL import Image
import time_machine

import app
from app import (
    app as flask_app, Kid, get_clanes, parse_iso_date,
    return_progress_color, TRANSLATIONS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_data():
    return [
        {"nombre": "Test Baby", "fecha": "2027-03-10", "clan": "test", "embarazo": True},
        {"nombre": "Alice", "fecha": "2018-07-15", "clan": "test"},
        {"nombre": "Bob", "fecha": "2015-11-22", "clan": "test"},
    ]


@pytest.fixture
def client():
    flask_app.secret_key = "test-secret"
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_clanes_cache(monkeypatch):
    monkeypatch.setattr(app, "_clanes_cache", None)
    monkeypatch.setattr(app, "_clanes_cache_time", 0.0)


@pytest.fixture
def auth_client(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
    return client


@pytest.fixture
def es():
    return TRANSLATIONS["es"]


@pytest.fixture
def ca():
    return TRANSLATIONS["ca"]


@pytest.fixture
def supabase_mock(monkeypatch):
    mock = MagicMock()
    kids_data = [
        {"nombre": "Alice", "fecha": "2018-07-15", "clan": "test", "embarazo": False, "image_url": None},
    ]
    mock.table.return_value.select.return_value.execute.return_value.data = kids_data
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value.data = kids_data
    mock.storage.from_.return_value.upload.return_value = None
    mock.storage.from_.return_value.get_public_url.return_value = (
        "https://proj.supabase.co/storage/v1/object/public/images/alice.jpeg"
    )
    monkeypatch.setattr("app.supabase_client", mock)
    return mock


def _make_jpeg(width=100, height=100, color="blue") -> io.BytesIO:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Translation files
# ---------------------------------------------------------------------------

def test_translations_load():
    assert "es" in TRANSLATIONS
    assert "ca" in TRANSLATIONS


def test_translations_have_same_keys():
    assert set(TRANSLATIONS["es"].keys()) == set(TRANSLATIONS["ca"].keys())


def test_translations_months_length():
    assert len(TRANSLATIONS["es"]["months"]) == 12
    assert len(TRANSLATIONS["ca"]["months"]) == 12


# ---------------------------------------------------------------------------
# Kid class
# ---------------------------------------------------------------------------

def test_kid_initialization(sample_data):
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
    assert kid.nombre == "Alice"
    assert isinstance(kid.cumple_date, date)
    assert 0 <= kid.progreso <= 100
    assert kid.fecha == date(2018, 7, 15)


def test_parse_iso_date():
    assert parse_iso_date("2017-09-25") == date(2017, 9, 25)
    assert parse_iso_date(date(2017, 9, 25)) == date(2017, 9, 25)


def test_kid_pregnancy(sample_data):
    kid = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, sample_data[0]["clan"], embarazo=True)
    assert kid.embarazo is True
    assert kid.edad == 0
    assert 0 <= kid.progreso <= 100


def test_kid_progress_bar_color():
    assert return_progress_color(10) == "progress-rojo-anaranjado h-5 rounded-full striped-progress-bar"
    assert return_progress_color(50) == "progress-verde-azulado h-5 rounded-full striped-progress-bar"
    assert return_progress_color(100) == "progress-purpura h-5 rounded-full striped-progress-bar"


def test_str_method(sample_data):
    meses = TRANSLATIONS["es"]["months"]
    with time_machine.travel(datetime(2026, 1, 1)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        assert str(kid) == f"Cumple {kid.edad} el {kid.cumple_date.day} de {meses[kid.cumple_date.month - 1]}"

        kid.cumple_today = True
        assert "Hoy cumple" in str(kid)

        kid_preg = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, sample_data[0]["clan"], embarazo=True)
        assert "Se espera para el" in str(kid_preg)


def test_progress_method(sample_data):
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
    _, cumple_date, progreso, _ = kid.progress()
    assert 0 <= progreso <= 100
    assert isinstance(cumple_date, date)

    kid_preg = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, sample_data[0]["clan"], embarazo=True)
    _, _, progreso_preg, _ = kid_preg.progress()
    assert progreso_preg != 0


def test_kid_nacimiento(sample_data):
    with time_machine.travel(datetime(2027, 3, 10)):
        kid = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 1, sample_data[0]["clan"])
        kid.cumple_today = True
        kid.progress()
        assert kid.nacimiento is True

        kid2 = Kid(sample_data[2]["nombre"], sample_data[2]["fecha"], 2, sample_data[2]["clan"])
        kid2.cumple_today = False
        kid2.progress()
        assert kid2.nacimiento is False


def test_file_existence(sample_data):
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
    assert kid.video is False
    assert kid.image == "static/images/placeholder/missing.jpg"


def test_kid_uses_image_url_when_provided(sample_data):
    url = "https://proj.supabase.co/storage/v1/object/public/images/alice.jpeg"
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"], image_url=url)
    assert kid.image == url


@pytest.mark.parametrize(
    ("today", "expected_date", "expected_age", "is_today"),
    [
        (datetime(2026, 7, 15), date(2026, 7, 15), 8, True),
        (datetime(2026, 7, 14), date(2026, 7, 15), 8, False),
        (datetime(2026, 7, 16), date(2027, 7, 15), 9, False),
        (datetime(2026, 12, 31), date(2027, 7, 15), 9, False),
        (datetime(2027, 1, 1), date(2027, 7, 15), 9, False),
    ],
)
def test_birthday_calendar_boundaries(today, expected_date, expected_age, is_today):
    with time_machine.travel(today):
        kid = Kid("Alice", "2018-07-15", 1, "test")
    assert kid.cumple_date == expected_date
    assert kid.edad == expected_age
    assert kid.cumple_today is is_today


def test_february_29_birthday_in_leap_year():
    with time_machine.travel(datetime(2028, 2, 29)):
        kid = Kid("Leap", "2020-02-29", 1, "test")
    assert kid.cumple_today is True
    assert kid.edad == 8


def test_february_29_birthday_in_non_leap_year():
    with time_machine.travel(datetime(2027, 2, 28)):
        kid = Kid("Leap", "2020-02-29", 1, "test")
    assert kid.cumple_today is True
    assert kid.cumple_date == date(2027, 2, 28)


def test_pregnancy_future_due_date():
    with time_machine.travel(datetime(2026, 1, 1)):
        kid = Kid("Baby", "2026-03-12", 1, "test", embarazo=True)
    assert kid.cumple_date == date(2026, 3, 12)
    assert 0 < kid.progreso < 100


def test_pregnancy_past_due_date():
    with time_machine.travel(datetime(2026, 3, 13)):
        kid = Kid("Baby", "2026-03-12", 1, "test", embarazo=True)
    assert kid.progreso == 100


# ---------------------------------------------------------------------------
# Kid.label(t) — i18n
# ---------------------------------------------------------------------------

def test_label_birthday_coming_es(sample_data, es):
    with time_machine.travel(datetime(2026, 1, 1)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        assert "Cumple" in kid.label(es)
        assert "Julio" in kid.label(es)


def test_label_birthday_coming_ca(sample_data, ca):
    with time_machine.travel(datetime(2026, 1, 1)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        assert "Compleix" in kid.label(ca)
        assert "Juliol" in kid.label(ca)


def test_label_pregnancy_es(sample_data, es):
    kid = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, sample_data[0]["clan"], embarazo=True)
    assert "Se espera" in kid.label(es)
    assert "Marzo" in kid.label(es)


def test_label_pregnancy_ca(sample_data, ca):
    kid = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, sample_data[0]["clan"], embarazo=True)
    assert "S'espera" in kid.label(ca)
    assert "Març" in kid.label(ca)


def test_label_birthday_today_es(sample_data, es):
    with time_machine.travel(datetime(2026, 7, 15)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        assert "Hoy cumple" in kid.label(es)


def test_label_birthday_today_ca(sample_data, ca):
    with time_machine.travel(datetime(2026, 7, 15)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        assert "Avui compleix" in kid.label(ca)


# ---------------------------------------------------------------------------
# Kid.display_name(t) — i18n
# ---------------------------------------------------------------------------

def test_display_name_normal(sample_data, es):
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
    assert kid.display_name(es) == "Alice"


def test_display_name_birthday_es(sample_data, es):
    with time_machine.travel(datetime(2026, 7, 15)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        assert "Felicidades" in kid.display_name(es)
        assert "Alice" in kid.display_name(es)


def test_display_name_birthday_ca(sample_data, ca):
    with time_machine.travel(datetime(2026, 7, 15)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        assert "Felicitats" in kid.display_name(ca)
        assert "Alice" in kid.display_name(ca)


def test_display_name_no_side_effect(sample_data, es):
    with time_machine.travel(datetime(2026, 7, 15)):
        kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1, sample_data[1]["clan"])
        kid.display_name(es)
        assert kid.nombre == "Alice"


# ---------------------------------------------------------------------------
# Route: / (index)
# ---------------------------------------------------------------------------

def test_index_redirects_unauthenticated(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_index_renders_authenticated(auth_client, supabase_mock):
    response = auth_client.get("/")
    assert response.status_code == 200
    assert "Cumple".encode() in response.data or "Compleix".encode() in response.data


def test_index_shows_success_banner(auth_client, supabase_mock):
    response = auth_client.get("/?uploaded=Alice")
    assert response.status_code == 200
    assert b"Alice" in response.data
    assert b"subida correctamente" in response.data


def test_index_catalan(auth_client, supabase_mock):
    with auth_client.session_transaction() as sess:
        sess["lang"] = "ca"
    response = auth_client.get("/")
    assert response.status_code == 200
    assert "Proper Aniversari".encode() in response.data


def test_index_catalan_success_banner(auth_client, supabase_mock):
    with auth_client.session_transaction() as sess:
        sess["lang"] = "ca"
    response = auth_client.get("/?uploaded=Alice")
    assert b"pujada correctament" in response.data


# ---------------------------------------------------------------------------
# Route: /set_language
# ---------------------------------------------------------------------------

def test_set_language_es(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
    client.get("/set_language/es")
    with client.session_transaction() as sess:
        assert sess.get("lang") == "es"


def test_set_language_ca(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
    client.get("/set_language/ca")
    with client.session_transaction() as sess:
        assert sess.get("lang") == "ca"


def test_set_language_invalid_ignored(client):
    client.get("/set_language/fr")
    with client.session_transaction() as sess:
        assert sess.get("lang") is None


def test_set_language_accessible_without_auth(client):
    response = client.get("/set_language/ca")
    assert response.status_code in (200, 302)


# ---------------------------------------------------------------------------
# Route: /login
# ---------------------------------------------------------------------------

def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"password" in response.data.lower()


def test_login_get_catalan(client):
    with client.session_transaction() as sess:
        sess["lang"] = "ca"
    response = client.get("/login")
    assert b"Contrasenya" in response.data


def test_login_post_wrong_password(client):
    with patch("app.PASSWORD", "correct"):
        response = client.post("/login", data={"password": "wrong"})
    assert response.status_code == 200
    assert "incorrecta".encode() in response.data


def test_login_post_correct_password(client):
    with patch("app.PASSWORD", "correct"):
        response = client.post("/login", data={"password": "correct"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


# ---------------------------------------------------------------------------
# Route: /upload
# ---------------------------------------------------------------------------

def test_upload_get_requires_auth(client):
    response = client.get("/upload")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_upload_get_renders_form(auth_client, supabase_mock):
    response = auth_client.get("/upload")
    assert response.status_code == 200
    assert "Subir foto".encode() in response.data


def test_upload_get_renders_form_catalan(auth_client, supabase_mock):
    with auth_client.session_transaction() as sess:
        sess["lang"] = "ca"
    response = auth_client.get("/upload")
    assert b"Pujar foto" in response.data


def test_upload_post_missing_fields(auth_client, supabase_mock):
    response = auth_client.post("/upload", data={})
    assert response.status_code == 400


def test_upload_post_success(auth_client, supabase_mock):
    buf = _make_jpeg()
    response = auth_client.post(
        "/upload",
        data={"nombre": "Alice", "image": (buf, "alice.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 302
    assert "uploaded=Alice" in response.headers["Location"]


def test_upload_post_success_calls_storage(auth_client, supabase_mock):
    buf = _make_jpeg()
    auth_client.post(
        "/upload",
        data={"nombre": "Alice", "image": (buf, "alice.jpg")},
        content_type="multipart/form-data",
    )
    supabase_mock.storage.from_.assert_called_with("images")
    supabase_mock.storage.from_.return_value.upload.assert_called_once()


def test_upload_post_success_updates_db(auth_client, supabase_mock):
    buf = _make_jpeg()
    auth_client.post(
        "/upload",
        data={"nombre": "Alice", "image": (buf, "alice.jpg")},
        content_type="multipart/form-data",
    )
    supabase_mock.table.return_value.update.assert_called_once()


def test_upload_post_storage_error(auth_client, supabase_mock):
    supabase_mock.storage.from_.return_value.upload.side_effect = Exception("bucket error")
    buf = _make_jpeg()
    response = auth_client.post(
        "/upload",
        data={"nombre": "Alice", "image": (buf, "alice.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 500
    assert b"bucket error" in response.data


def test_upload_normalizes_accented_name(auth_client, supabase_mock):
    buf = _make_jpeg()
    auth_client.post(
        "/upload",
        data={"nombre": "Míriam", "image": (buf, "miriam.jpg")},
        content_type="multipart/form-data",
    )
    call_kwargs = supabase_mock.storage.from_.return_value.upload.call_args
    assert "miriam.jpeg" in str(call_kwargs)


# ---------------------------------------------------------------------------
# Image crop (1:1 centered)
# ---------------------------------------------------------------------------

def _crop(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    return img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))


def test_crop_horizontal_gives_square():
    assert _crop(Image.new("RGB", (1200, 800))).size == (800, 800)


def test_crop_vertical_gives_square():
    assert _crop(Image.new("RGB", (600, 900))).size == (600, 600)


def test_crop_square_unchanged():
    assert _crop(Image.new("RGB", (500, 500))).size == (500, 500)


def test_crop_is_centered():
    img = Image.new("RGB", (300, 100), color=(0, 0, 255))
    for x in range(100, 200):
        for y in range(100):
            img.putpixel((x, y), (255, 0, 0))

    cropped = _crop(img)
    assert cropped.size == (100, 100)
    assert cropped.getpixel((50, 50)) == (255, 0, 0)


# ---------------------------------------------------------------------------
# Clans cache
# ---------------------------------------------------------------------------

def _clanes_client(data=None, error=None):
    mock = MagicMock()
    query = mock.table.return_value.select.return_value.execute
    if error:
        query.side_effect = error
    else:
        query.return_value.data = data
    return mock


def test_get_clanes_initial_load_and_cache(monkeypatch):
    client = _clanes_client([{"clan": "mc", "clan_name": "Marín Codina"}])
    monkeypatch.setattr(app, "supabase_client", client)
    monkeypatch.setattr(app.time, "monotonic", MagicMock(side_effect=[100.0, 101.0]))

    assert get_clanes()[0]["clan"] == "mc"
    assert get_clanes()[0]["clan"] == "mc"
    client.table.assert_called_once_with("clanes")


def test_get_clanes_refreshes_after_ttl(monkeypatch):
    client = _clanes_client([{"clan": "mc"}])
    monkeypatch.setattr(app, "supabase_client", client)
    monkeypatch.setattr(
        app.time,
        "monotonic",
        MagicMock(side_effect=[100.0, 100.0 + app.CLANES_CACHE_TTL_SECONDS + 1]),
    )

    get_clanes()
    get_clanes()
    assert client.table.call_count == 2


def test_get_clanes_returns_stale_cache_on_refresh_failure(monkeypatch):
    client = _clanes_client(error=RuntimeError("offline"))
    monkeypatch.setattr(app, "supabase_client", client)
    monkeypatch.setattr(app, "_clanes_cache", [{"clan": "mc"}])
    monkeypatch.setattr(app, "_clanes_cache_time", 0.0)
    monkeypatch.setattr(app.time, "monotonic", lambda: app.CLANES_CACHE_TTL_SECONDS + 1)

    assert get_clanes() == [{"clan": "mc"}]


def test_get_clanes_returns_empty_without_cache_on_failure(monkeypatch):
    monkeypatch.setattr(app, "supabase_client", _clanes_client(error=RuntimeError("offline")))
    assert get_clanes() == []


def test_get_clanes_without_configured_client(monkeypatch):
    monkeypatch.setattr(app, "supabase_client", None)
    assert get_clanes() == []


def test_import_has_no_supabase_query():
    env = os.environ.copy()
    env.pop("SUPABASE_URL", None)
    env.pop("SUPABASE_SERVICE_ROLE_KEY", None)
    result = subprocess.run(
        [sys.executable, "-c", "import app"],
        cwd=os.path.dirname(app.__file__),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
