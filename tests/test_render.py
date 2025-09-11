import json
import pytest
from datetime import datetime, date
from render import Kid, return_progress_color, generate_kids_page
from unittest.mock import patch, mock_open
import time_machine


@pytest.fixture
def sample_data():
    return [
        {"nombre": "Test Baby", "fecha": "10/03/2024", "embarazo": True},
        {"nombre": "Alice", "fecha": "15/07/2018"},
        {"nombre": "Bob", "fecha": "22/11/2015"}
    ]

def test_kid_initialization(sample_data):
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1)
    assert kid.nombre == "Alice"
    assert isinstance(kid.cumple_date, datetime)
    assert 0 <= kid.progreso <= 100

def test_kid_pregnancy(sample_data):
    kid = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, embarazo=True)
    assert kid.embarazo is True
    assert kid.edad == 0  # The age should be 0 as the child is still in pregnancy
    assert 0 <= kid.progreso <= 100  # Progreso will be calculated based on the due date

def test_kid_progress_bar_color():
    # Testing for valid return value based on progress value
    assert return_progress_color(10) == 'progress-rojo-anaranjado h-5 rounded-full striped-progress-bar'
    assert return_progress_color(50) == 'progress-verde-azulado h-5 rounded-full striped-progress-bar'
    assert return_progress_color(100) == 'progress-purpura h-5 rounded-full striped-progress-bar'

def test_str_method(sample_data):
    # Test Kid's `__str__` method
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1)
    assert str(kid) == f"Cumple {str(kid.edad)}  el {kid.cumple_date.day} de {meses[kid.cumple_date.month - 1]}"

    # Test Kid when today is the birthday
    kid.cumple_today = True
    assert "Hoy cumple" in str(kid)

    # Test Kid with pregnancy
    kid_preg = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, embarazo=True)
    assert "Se espera para el" in str(kid_preg)

def test_progress_method(sample_data):
    # Test Kid's progress method, including edge cases for pregnancy and age
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1)
    age, cumple_date, progreso, cumple_today = kid.progress()
    assert 0 <= progreso <= 100
    assert isinstance(cumple_date, datetime)

    # This should return 0 as the pregnancy is still ongoing
    kid_preg = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 2, embarazo=True)
    edad, fecha_parto, progreso, cumple_today = kid_preg.progress()
    assert progreso != 0


def test_kid_nacimiento(sample_data):
    today = datetime(2024, 3, 10)
    with time_machine.travel(today):   
        # Test for kids' nacimiento flag when today's date matches birthdate
        kid = Kid(sample_data[0]["nombre"], sample_data[0]["fecha"], 1)  # Crea un niño (Alice)
        kid.cumple_today = True
        kid.progress()  # Llama al método progress para establecer la bandera de nacimiento
        
        # Comprobamos si la fecha de nacimiento es la misma que hoy y si `nacimiento` es True
        assert kid.nacimiento is True  # La bandera de `nacimiento` debería ser True si la fecha coincide con el cumpleaños

        # Si no es el día de su nacimiento, la bandera de nacimiento debe ser False
        kid2 = Kid(sample_data[2]["nombre"], sample_data[2]["fecha"], 2)  # Otro niño (Bob)
        kid2.cumple_today = False
        kid2.progress()  # Llamamos al método progress para no tener `nacimiento` activo
        assert kid2.nacimiento is False  # La bandera `nacimiento` debe ser False para el segundo niño

def test_file_existence(sample_data):
    # Test for file existence for videos and images
    kid = Kid(sample_data[1]["nombre"], sample_data[1]["fecha"], 1)

    # Mock os.path.exists to always return True or False based on file presence
    with patch("os.path.exists") as mock_exists:
        # Test for video existence

        mock_exists.return_value = False
        assert kid.video is False

        # Test for image existence
        mock_exists.return_value = True
        assert kid.image is not None  # Image should be set to a valid path
        mock_exists.return_value = False
        assert kid.image == 'static/images/placeholder/missing.jpg'  # If no image exists, fallback to missing image


@patch("builtins.open", new_callable=mock_open)
@patch("json.load")
@patch("jinja2.Environment.get_template")
def test_generate_kids_page(mock_get_template, mock_json_load, mock_open, sample_data):
    # Simulamos que `json.load` devuelve la lista de sample_data
    mock_json_load.return_value = sample_data

    # Simulamos un template que retorna una cadena
    mock_template = mock_get_template.return_value
    mock_template.render.return_value = "HTML content"

    # Llamamos a la función que estamos probando
    generate_kids_page()

    # Verificamos que el archivo 'data.json' fue abierto para leer
    mock_open.assert_any_call("data.json", encoding='utf-8')
    # Verificamos que el archivo 'public/index.html' fue abierto para escribir
    mock_open.assert_any_call("public/index.html", "w", encoding='utf-8')

    # Comprobamos que `json.load` fue llamado para cargar los datos
    mock_json_load.assert_called_once()

    # Verificamos que el contenido HTML fue escrito en el archivo
    mock_open().write.assert_called_once_with("HTML content")
