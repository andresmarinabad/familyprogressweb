"""
Render index.html with the kids data.
"""
import os
import json
from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader

meses = ['Enero',
         'Febrero',
         'Marzo',
         'Abril',
         'Mayo',
         'Junio',
         'Julio',
         'Agosto',
         'Septiembre',
         'Octubre',
         'Noviembre',
         'Diciembre'
         ]


def return_progress_color(progreso, today=False):
    """
    Returns the CSS class for the progress bar based on the progress value.
    """
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
        if progreso < threshold:
            return f"{class_name} h-5 rounded-full striped-progress-bar"


class Kid:
    """
    A class to represent a kid and track their progress.
    """
    def __init__(self, nombre, fecha, num, embarazo=False):
        self.nombre = nombre
        self.fecha = fecha
        self.embarazo = embarazo
        self.nacimiento = False
        self.edad, self.cumple_date, self.progreso, self.cumple_today = self.progress()
        self.dorsal = num
        self.color = return_progress_color(self.progreso, self.cumple_today)
        self.video = os.path.exists(f"public/static/videos/{self.nombre.lower()}.mp4")
        self.image = self.get_image()

    def __str__(self):
        dia = self.cumple_date.day
        mes = meses[self.cumple_date.month - 1]
        if self.embarazo:
            return f"Se espera para el {dia} de {mes}"

        if self.cumple_today:
            self.nombre = f"¡Felicidades a {self.nombre}!"
            if self.edad == 0:
                return "Hoy has nacido"
            elif self.edad == 1:
                return "Hoy cumple 1 año"
            return f"Hoy cumple {str(self.edad)} años"

        return f"Cumple {str(self.edad)}  el {dia} de {mes}"

    def get_image(self):
        """
        Return the image path based on the kid's age or pregnancy status.
        """
        if os.path.exists(f"public/static/images/{self.nombre.lower()}.jpeg"):
            return f"static/images/{self.nombre.lower()}.jpeg"

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
        """
        Calculate the progress of pregnancy or age based on the given date.
        """
        today = datetime.today()

        if self.embarazo:
            fecha_parto = datetime.strptime(self.fecha, '%d/%m/%Y')
            if fecha_parto.date() < today.date():
                dif_dates = 0
            else:
                dif_dates = (fecha_parto - today).days
            return 0, fecha_parto, int(((270 - dif_dates)/270) * 100), False

        fecha_nac = datetime.strptime(self.fecha, '%d/%m/%Y')
        self.nacimiento = fecha_nac.date() == today.date() and not self.embarazo

        current_year = date.today().year
        parts = self.fecha.split('/')
        cumple = f'{parts[0]}/{parts[1]}/{current_year}'

        cumple_date = datetime.strptime(cumple, '%d/%m/%Y')

        edad = current_year - int(parts[2])

        if today.date() == cumple_date.date():
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year}'
            return edad, cumple_date, 100, True
        if today.date() > cumple_date.date():
            edad += 1
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year+1}'
            cumple_date = datetime.strptime(self.fecha, '%d/%m/%Y')
        else:
            self.fecha = f'{parts[0]}/{parts[1]}/{current_year}'

        dif_dates = (cumple_date - today).days

        return edad, cumple_date, int(((365 - dif_dates)/365) * 100), False


if __name__ == '__main__':

    kids = []
    with open("data.json", encoding='utf-8') as f:
        data = json.load(f)

    for dorsal, objeto in enumerate(data, start=1):
        try:
            kids.append(Kid(objeto['nombre'], objeto['fecha'], dorsal, objeto['embarazo']))
        except KeyError:
            kids.append(Kid(objeto['nombre'], objeto['fecha'], dorsal))

    kids.sort(key=lambda x: x.cumple_date, reverse=False)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("index.html")
    output = template.render(kids=kids)
    with open("public/index.html", "w", encoding='utf-8') as f:
        f.write(output)
