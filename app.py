"""
Render index.html with the kids data.
"""
import os
import json
import io
from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader
import unicodedata
from zoneinfo import ZoneInfo
import resend
from PIL import Image
from supabase import create_client, Client

from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4 MB (límite de Vercel)

PASSWORD = os.getenv("APP_PASSWORD")

_supabase_url = os.getenv("SUPABASE_URL")
_supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client: Client | None = (
    create_client(_supabase_url, _supabase_key)
    if _supabase_url and _supabase_key
    else None
)


def _load_translations():
    base = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for lang in ("es", "ca"):
        path = os.path.join(base, "translations", f"{lang}.json")
        with open(path, encoding="utf-8") as f:
            out[lang] = json.load(f)
    return out


TRANSLATIONS = _load_translations()


def get_lang():
    lang = session.get("lang")
    if lang in TRANSLATIONS:
        return lang
    accept = request.headers.get("Accept-Language", "")
    if accept[:2].lower() == "ca":
        return "ca"
    return "es"


def _normalize_name(nombre):
    nfkd_form = unicodedata.normalize('NFD', nombre.lower())
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def return_progress_color(progreso, today=False):
    progress_classes = [
        (5, 'progress-rojo-intenso'),
        (10, 'progress-rojo-anaranjado'),
        (15, 'progress-naranja-oscuro'),
        (20, 'progress-naranja-claro'),
        (25, 'progress-amarillo-dorado'),
        (30, 'progress-amarillo-verdoso'),
        (35, 'progress-verde-claro'),
        (40, 'progress-verde-lima'),
        (45, 'progress-verde-intenso'),
        (50, 'progress-verde-azulado'),
        (55, 'progress-turquesa'),
        (60, 'progress-cian'),
        (65, 'progress-azul-claro'),
        (70, 'progress-azul-cielo'),
        (75, 'progress-azul-medio'),
        (80, 'progress-azul-intenso'),
        (85, 'progress-azul-oscuro'),
        (90, 'progress-indigo'),
        (95, 'progress-violeta'),
        (101, 'progress-purpura')
    ]

    if today:
        return 'progress-gold h-5 rounded-full'
    for threshold, class_name in progress_classes:
        if progreso <= threshold:
            return f"{class_name} h-5 rounded-full striped-progress-bar"


def comprobar_lista():
    hoy = datetime.now()
    response = supabase_client.table("kids").select("nombre, fecha").execute()
    for persona in response.data:
        fecha_persona = datetime.strptime(persona['fecha'], '%d/%m/%Y')
        if hoy.day == fecha_persona.day and hoy.month == fecha_persona.month:
            edad = hoy.year - fecha_persona.year
            return {"nombre": persona['nombre'], "edad": edad}
    return None


class Kid:
    def __init__(self, nombre, fecha, num, clan, embarazo=False, image_url=None):
        self.nombre = nombre
        self.fecha = fecha
        self.embarazo = embarazo
        self.nacimiento = False
        self.edad, self.cumple_date, self.progreso, self.cumple_today = self.progress()
        self.dorsal = num
        self.clan = clan
        self.color = return_progress_color(self.progreso, self.cumple_today)
        self.video = os.path.exists(f"static/videos/{self.normalized_name()}.mp4")
        self.normalized = self.normalized_name()
        self._image_url = image_url
        self.image = self.get_image()

    def label(self, t):
        dia = self.cumple_date.day
        mes = t["months"][self.cumple_date.month - 1]
        if self.embarazo:
            return t["expected"].format(day=dia, month=mes)
        if self.cumple_today:
            if self.edad == 0:
                return t["born_today"]
            if self.edad == 1:
                return t["birthday_today_1"]
            return t["birthday_today"].format(age=self.edad)
        return t["birthday_coming"].format(age=self.edad, day=dia, month=mes)

    def display_name(self, t):
        if self.cumple_today:
            return t["congrats"].format(name=self.nombre)
        return self.nombre

    def __str__(self):
        return self.label(TRANSLATIONS["es"])

    def get_image(self):
        if self._image_url:
            return self._image_url

        if self.embarazo:
            fpp = datetime.strptime(self.fecha, "%d/%m/%Y")
            hoy = datetime.today()
            semanas_restantes = (fpp - hoy).days // 7
            semanas_actuales = 40 - semanas_restantes

            if semanas_actuales < 10:
                return "static/images/placeholder/1.png"
            elif semanas_actuales < 20:
                return "static/images/placeholder/2.png"
            elif semanas_actuales < 30:
                return "static/images/placeholder/3.png"
            else:
                return "static/images/placeholder/4.png"

        return "static/images/placeholder/missing.jpg"

    def progress(self):
        today = datetime.now(ZoneInfo("Europe/Madrid")).date()

        if self.embarazo:
            fecha_parto = datetime.strptime(self.fecha, '%d/%m/%Y').date()
            if fecha_parto < today:
                dif_dates = 0
            else:
                dif_dates = (fecha_parto - today).days
            return 0, fecha_parto, int(((270 - dif_dates)/270) * 100), False

        fecha_nac = datetime.strptime(self.fecha, '%d/%m/%Y').date()
        self.nacimiento = fecha_nac == today and not self.embarazo

        current_year = date.today().year
        parts = self.fecha.split('/')
        cumple = f'{parts[0]}/{parts[1]}/{current_year}'
        cumple_date = datetime.strptime(cumple, '%d/%m/%Y').date()
        edad = current_year - int(parts[2])

        if today == cumple_date:
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year}'
            return edad, cumple_date, 100, True
        if today > cumple_date:
            edad += 1
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year+1}'
            cumple_date = datetime.strptime(self.fecha, '%d/%m/%Y').date()
        else:
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year}'

        dif_dates = (cumple_date - today).days
        return edad, cumple_date, int(((365 - dif_dates)/365) * 100), False

    def normalized_name(self):
        return _normalize_name(self.nombre)


@app.route('/')
def generate_kids_page():
    response = supabase_client.table("kids").select("*").execute()
    kids = []
    for dorsal, obj in enumerate(response.data, start=1):
        kids.append(Kid(
            obj['nombre'], obj['fecha'], dorsal, obj['clan'],
            obj.get('embarazo', False), obj.get('image_url'),
        ))

    kids.sort(key=lambda x: x.cumple_date)

    lang = get_lang()
    t = TRANSLATIONS[lang]
    uploaded = request.args.get('uploaded')

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("index.html")
    return template.render(kids=kids, uploaded=uploaded, t=t, lang=lang)


@app.route("/login", methods=["GET", "POST"])
def login():
    lang = get_lang()
    t = TRANSLATIONS[lang]
    error = None

    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session.permanent = True
            session["logged_in"] = True
            return redirect("/")
        error = t["login_error"]

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("login.html")
    return template.render(error=error, t=t, lang=lang)


@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in TRANSLATIONS:
        session["lang"] = lang
    return redirect(request.referrer or "/")


@app.before_request
def protect_routes():
    if request.path.startswith("/static/"):
        return
    if request.endpoint in {"login", "set_language"}:
        return
    if not session.get("logged_in"):
        return redirect("/login")


@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    response = supabase_client.table("kids").select("nombre").execute()
    nombres = [obj['nombre'] for obj in response.data]

    lang = get_lang()
    t = TRANSLATIONS[lang]
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("upload.html")

    if request.method == 'GET':
        return template.render(nombres=nombres, t=t, lang=lang)

    nombre = request.form.get('nombre')
    file = request.files.get('image')

    if not nombre or not file or file.filename == '':
        return template.render(nombres=nombres, t=t, lang=lang, error=t["error_missing_fields"]), 400

    storage_path = f"{_normalize_name(nombre)}.jpeg"
    app.logger.info("Procesando imagen para %s -> %s", nombre, storage_path)

    try:
        img = Image.open(file.stream).convert('RGB')
        w, h = img.size
        side = min(w, h)
        img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        image_bytes = buf.getvalue()
    except Exception as e:
        app.logger.error("Error procesando imagen: %s", e)
        return template.render(nombres=nombres, t=t, lang=lang, error=t["error_image"].format(detail=e)), 500

    try:
        supabase_client.storage.from_("images").upload(
            path=storage_path,
            file=image_bytes,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )
    except Exception as e:
        app.logger.error("Error subiendo imagen a Supabase Storage: %s", e)
        return template.render(nombres=nombres, t=t, lang=lang, error=t["error_storage"].format(detail=e)), 500

    public_url = supabase_client.storage.from_("images").get_public_url(storage_path)
    supabase_client.table("kids").update({"image_url": public_url}).eq("nombre", nombre).execute()

    return redirect(f'/?uploaded={nombre}')


if __name__ == '__main__':
    app.run()
