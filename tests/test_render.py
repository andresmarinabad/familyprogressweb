import json
import pytest
import io
import os
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from PIL import Image
import time_machine

from app import app as flask_app, Kid, return_progress_color, TRANSLATIONS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_data():
    return [
        {"nombre": "Test Baby", "fecha": "10/03/2024", "clan": "test", "embarazo": True},
        {"nombre": "Alice", "fecha": "15/07/2018", "clan": "test"},
        {"nombre": "Bob", "fecha": "22/11/2015", "clan": "test"},
    ]


@pytest.fixture
def client():
    flask_app.secret_key = "test-secret"
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


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
    with time_machine.travel(datetime(2024, 3, 10)):
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


def test_index_renders_authenticated(auth_client):
    response = auth_client.get("/")
    assert response.status_code == 200
    assert "Cumple".encode() in response.data or "Compleix".encode() in response.data


def test_index_shows_success_banner(auth_client):
    response = auth_client.get("/?uploaded=Alice")
    assert response.status_code == 200
    assert b"Alice" in response.data
    assert b"subida correctamente" in response.data


def test_index_catalan(auth_client):
    with auth_client.session_transaction() as sess:
        sess["lang"] = "ca"
    response = auth_client.get("/")
    assert response.status_code == 200
    assert "Proper Aniversari".encode() in response.data


def test_index_catalan_success_banner(auth_client):
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


def test_upload_get_renders_form(auth_client):
    response = auth_client.get("/upload")
    assert response.status_code == 200
    assert "Subir foto".encode() in response.data


def test_upload_get_renders_form_catalan(auth_client):
    with auth_client.session_transaction() as sess:
        sess["lang"] = "ca"
    response = auth_client.get("/upload")
    assert b"Pujar foto" in response.data


def test_upload_post_missing_fields(auth_client):
    response = auth_client.post("/upload", data={})
    assert response.status_code == 400


def test_upload_post_no_token(auth_client):
    buf = _make_jpeg()
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("GITHUB_TOKEN", None)
        response = auth_client.post(
            "/upload",
            data={"nombre": "Alice", "image": (buf, "alice.jpg")},
            content_type="multipart/form-data",
        )
    assert response.status_code == 500
    assert b"GITHUB_TOKEN" in response.data


def test_upload_post_success(auth_client):
    buf = _make_jpeg()
    mock_get = MagicMock(status_code=404)
    mock_put = MagicMock(status_code=201)

    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
        with patch("app.requests.get", return_value=mock_get):
            with patch("app.requests.put", return_value=mock_put):
                response = auth_client.post(
                    "/upload",
                    data={"nombre": "Alice", "image": (buf, "alice.jpg")},
                    content_type="multipart/form-data",
                )

    assert response.status_code == 302
    assert "uploaded=Alice" in response.headers["Location"]


def test_upload_post_github_error(auth_client):
    buf = _make_jpeg()
    mock_get = MagicMock(status_code=404)
    mock_put = MagicMock(status_code=403, content=b'{"message":"Forbidden"}')
    mock_put.json.return_value = {"message": "Forbidden"}

    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
        with patch("app.requests.get", return_value=mock_get):
            with patch("app.requests.put", return_value=mock_put):
                response = auth_client.post(
                    "/upload",
                    data={"nombre": "Alice", "image": (buf, "alice.jpg")},
                    content_type="multipart/form-data",
                )

    assert response.status_code == 500
    assert b"Error GitHub" in response.data


def test_upload_includes_sha_when_file_exists(auth_client):
    buf = _make_jpeg()
    mock_get = MagicMock(status_code=200)
    mock_get.json.return_value = {"sha": "abc123"}

    captured = {}

    def fake_put(url, headers, json):
        captured["body"] = json
        return MagicMock(status_code=200)

    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
        with patch("app.requests.get", return_value=mock_get):
            with patch("app.requests.put", side_effect=fake_put):
                auth_client.post(
                    "/upload",
                    data={"nombre": "Alice", "image": (buf, "alice.jpg")},
                    content_type="multipart/form-data",
                )

    assert captured["body"]["sha"] == "abc123"


def test_upload_normalizes_accented_name(auth_client):
    buf = _make_jpeg()
    mock_get = MagicMock(status_code=404)
    mock_put = MagicMock(status_code=201)
    captured_url = {}

    def fake_get(url, headers):
        captured_url["url"] = url
        return mock_get

    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}):
        with patch("app.requests.get", side_effect=fake_get):
            with patch("app.requests.put", return_value=mock_put):
                auth_client.post(
                    "/upload",
                    data={"nombre": "Míriam", "image": (buf, "miriam.jpg")},
                    content_type="multipart/form-data",
                )

    assert "miriam.jpeg" in captured_url["url"]


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
