import json
from browser import document
from datetime import date, datetime


def get_hidden_number(item):
    return int(item.select_one(".hidden-number").text)


class Kid:
    def __init__(self, nombre, fecha, embarazo=False):
        self.nombre = nombre
        self.fecha = fecha
        self.foto = f'static/images/{nombre.lower()}.jpeg'
        self.embarazo = embarazo
        self.edad, self.cumple_date, self.progreso = self.progress()
    
    def __str__(self):
        if self.embarazo:
            return f"Fecha de parto {self.fecha}"
        return f"Cumple {str(self.edad)}  el {self.cumple_date.strftime('%d/%m/%Y')}"
    
    def progress(self):
        today = datetime.today()

        if self.embarazo:
            fecha_parto = datetime.strptime(self.fecha, '%d/%m/%Y')
            dif_dates = (fecha_parto - today).days
            return 0, fecha_parto, int(((270 - dif_dates)/270) * 100)

        current_year = date.today().year
        parts = self.fecha.split('/')
        cumple = f'{parts[0]}/{parts[1]}/{current_year}'

        cumple_date = datetime.strptime(cumple, '%d/%m/%Y')

        edad = current_year - int(parts[2])

        if today >= cumple_date:
            edad += 1
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year+1}'
            cumple_date = datetime.strptime(self.fecha, '%d/%m/%Y')
        else:
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year}'
        
        dif_dates = (cumple_date - today).days
        return edad, cumple_date, int(((365 - dif_dates)/365) * 100)


kids = []

div_kid = document["kid"]
div_kid.removeAttribute("hidden")
contenedor = document["contenedor"]
contenedor.clear()

data_file = "static/json/data.json"
data = json.load(open(data_file))

for objeto in data:
    try:
        kids.append(Kid(objeto['nombre'], objeto['fecha'], objeto['embarazo']))
    except KeyError:
        kids.append(Kid(objeto['nombre'], objeto['fecha']))

kids.sort(key=lambda x: x.progreso, reverse=True)


for kid in kids:
    new_div_kid = div_kid.cloneNode(True)
    
    foto_link = new_div_kid.querySelector(".card-img-top")
    foto_link.src = kid.foto

    name_header = new_div_kid.querySelector(".card-title")
    name_header.text = kid.nombre

    cumple_header = new_div_kid.querySelector(".card-subtitle")
    cumple_header.text = f"{kid}"

    progress_div = new_div_kid.querySelector(".auxbar")
    progress_div.style.width = f"{str(kid.progreso)}%"

    hidden_span = new_div_kid.querySelector(".hidden-number")
    hidden_span.text = kid.progreso

    if kid.progreso == 100:
        name_header.text = f"¡Felicidades a {kid.nombre}!"
        cumple_header.text = f"Hoy cumple {kid.edad} años"

    if kid.progreso < 5:
        progress_div.class_name = 'progress-rojo-intenso h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 10:
        progress_div.class_name = 'progress-rojo-anaranjado h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 15:
        progress_div.class_name = 'progress-naranja-oscuro h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 20:
        progress_div.class_name = 'progress-naranja-claro h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 25:
        progress_div.class_name = 'progress-amarillo-dorado h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 30:
        progress_div.class_name = 'progress-amarillo-verdoso h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 35:
        progress_div.class_name = 'progress-verde-claro h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 40:
        progress_div.class_name = 'progress-verde-lima h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 45:
        progress_div.class_name = 'progress-verde-intenso h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 50:
        progress_div.class_name = 'progress-verde-azulado h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 55:
        progress_div.class_name = 'progress-turquesa h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 60:
        progress_div.class_name = 'progress-cian h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 65:
        progress_div.class_name = 'progress-azul-claro h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 70:
        progress_div.class_name = 'progress-azul-cielo h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 75:
        progress_div.class_name = 'progress-azul-medio h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 80:
        progress_div.class_name = 'progress-azul-intenso h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 85:
        progress_div.class_name = 'progress-azul-oscuro h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 90:
        progress_div.class_name = 'progress-indigo h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 95:
        progress_div.class_name = 'progress-violeta h-5 rounded-full striped-progress-bar'
    elif kid.progreso < 100:
        progress_div.class_name = 'progress-purpura h-5 rounded-full striped-progress-bar'
    else:
        progress_div.class_name = 'progress-gold h-5 rounded-full striped-progress-bar'

    contenedor.appendChild(new_div_kid)
