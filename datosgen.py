import csv
import random
from faker import Faker

fake = Faker('es_ES')

def random_medication():
    return random.choice(['Enalapril', 'Prednisona', 'Salbutamol', 'Ibuprofeno', 'Metformina', 'Atorvastatina', 'Paracetamol', 'Amoxicilina', 'Omlodipino', 'Losartán', 'Aspirina', 'Omeprazol', 'Clopidogrel', 'Captopril', 'Furosemida'])

def random_procedure():
    return random.choice(['Laboratorio', 'Radiografía', 'Ecografía', 'Endoscopia', 'Tomografía', 'Resonancia magnética', 'Biopsia', 'Espirometría', 'Electrocardiograma', 'Densitometría ósea'])

def random_exam():
    return random.choice(['140/90', '3.4', '125/80', '110/70', '5.6', '120/80', '4.5', '130/85', '2.8', '7.9'])

def random_diagnosis():
    return random.choice(['Diabetes', 'Hipertensión', 'Artritis', 'Asma', 'Obesidad', 'Depresión', 'Ansiedad', 'Osteoporosis', 'Insuficiencia renal', 'Enfermedad cardíaca', 'Alzheimer', 'Cáncer', 'Esclerosis múltiple'])

def random_nse():
    nse_probs = [1, 9, 28.5, 26.2, 35.3]
    nse_values = ['A', 'B', 'C', 'D', 'E']
    return random.choices(nse_values, weights=nse_probs, k=1)[0]

def random_language():
    lang_probs = [83.11, 10.92, 1.67]
    lang_values = ['español', 'quechua', 'aimara']
    return random.choices(lang_values, weights=lang_probs, k=1)[0]

def random_race():
    race_probs = [60.2, 25.8, 5.9, 3.6, 1.2, 3.3]
    race_values = ['Mestizo', 'Amerindio', 'Blanco', 'Negro', 'Asiático', 'Otros']
    return random.choices(race_values, weights=race_probs, k=1)[0]

def random_location():
    locations_lima = [
    {'city': 'Lima', 'latitude': -12.0464, 'longitude': -77.0428},
    {'city': 'San Isidro', 'latitude': -12.0989, 'longitude': -77.0365},
    {'city': 'Miraflores', 'latitude': -12.1111, 'longitude': -77.0301},
    {'city': 'Barranco', 'latitude': -12.1409, 'longitude': -77.0208},
    {'city': 'La Molina', 'latitude': -12.0761, 'longitude': -76.9647},
    {'city': 'San Miguel', 'latitude': -12.0775, 'longitude': -77.0802},
    {'city': 'Santiago de Surco', 'latitude': -12.1251, 'longitude': -76.9988},
    {'city': 'San Borja', 'latitude': -12.0892, 'longitude': -76.9976},
    ]

    locations_provinces = [
        {'city': 'Arequipa', 'latitude': -16.4090, 'longitude': -71.5375},
        {'city': 'Trujillo', 'latitude': -8.1092, 'longitude': -79.0215},
        {'city': 'Cusco', 'latitude': -13.5319, 'longitude': -71.9673},
        {'city': 'Piura', 'latitude': -5.1945, 'longitude': -80.6328},
        {'city': 'Iquitos', 'latitude': -3.7437, 'longitude': -73.2516},
        {'city': 'Chiclayo', 'latitude': -6.7766, 'longitude': -79.8443},
        {'city': 'Huancayo', 'latitude': -12.0672, 'longitude': -75.2045},
        {'city': 'Tacna', 'latitude': -18.0056, 'longitude': -70.2463},
    ] # Agrega más ciudades fuera de Lima aquí

    if random.random() < 0.7:  # 70% de probabilidad de elegir una ubicación en Lima
        location = random.choice(locations_lima)
    else:  # 30% de probabilidad de elegir una ubicación fuera de Lima
        location = random.choice(locations_provinces)

    return location['city'], location['latitude'], location['longitude']

num_records = 10000
output_file = 'datos_med.csv'

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id_paciente', 'edad', 'genero', 'raza', 'ubicacion_geografica','latitud','longitud',
              'nivel_socioeconomico', 'idioma', 'enfermedades_cronicas',
              'diagnosticos_previos', 'resultados_examenes', 'tratamientos_ant',
              'fecha_visita', 'duracion_visita', 'tipo_tratamiento',
              'medicamentos_recetados', 'procedimientos_realizados',
              'resultados_pruebas_lab', 'facturacion', 'pago_seguros',
              'costo_tratamiento', 'id_centro_salud', 'camas_hospital',
              'medico_disponibles', 'enfermeras_disponibles', 'equipos_medicos',
              'suministros', 'tasa_exito_tratamiento', 'satisfaccion_paciente',
              'tasas_mortalidad', 'tasas_morbilidad', 'seguridad_paciente',
              'indicadores_desempenio', 'costos_operacion', 'recursos_humanos',
              'visitas_seguimiento', 'cumplimiento_recomendaciones',
              'seguimiento_enfermedad', 'eventos_adversos',
              'reclamaciones_responsabilidad_medica', 'incidentes_seguridad_paciente',
              'ensayos_clinicos', 'publicaciones_cientificas', 'descubrimientos_medicos']

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(num_records):
        city, latitude, longitude = random_location()
        writer.writerow({'id_paciente': i + 1,
                         'edad': random.randint(18, 100),
                         'genero': fake.random_element(elements=('M', 'F')),
                         'raza': random_race(),
                         'ubicacion_geografica': city,
                         'latitud': latitude,
                         'longitud': longitude,
                         'nivel_socioeconomico': random_nse(),
                         'idioma': random_language(),
                         'enfermedades_cronicas': random_diagnosis(),
                         'diagnosticos_previos': random_diagnosis(),
                         'resultados_examenes': random_exam(),
                         'tratamientos_ant': random_medication(),
                         'fecha_visita': fake.date_between(start_date='-1y', end_date='today'),
                         'duracion_visita': random.randint(15, 60),
                         'tipo_tratamiento': 'Medicación',
                         'medicamentos_recetados': random_medication(),
                         'procedimientos_realizados': random_procedure(),
                         'resultados_pruebas_lab': random.randint(100, 200),
                         'facturacion': random.randint(800, 3000),
                         'pago_seguros': random.randint(500, 2500),
                         'costo_tratamiento': random.randint(300, 2000),
                         'id_centro_salud': random.randint(1, 10),
                         'camas_hospital': random.randint(50, 200),
                         'medico_disponibles': random.randint(3, 15),
                         'enfermeras_disponibles': random.randint(3, 20),
                         'equipos_medicos': random.randint(2, 10),
                         'suministros': random.randint(50, 200),
                         'tasa_exito_tratamiento': random.uniform(70, 100),
                         'satisfaccion_paciente': random.uniform(70, 100),
                         'tasas_mortalidad': random.uniform(0.01, 0.1),
                         'tasas_morbilidad': random.uniform(0.01, 0.1),
                         'seguridad_paciente': random.uniform(80, 100),
                         'indicadores_desempenio': random.uniform(70, 100),
                         'costos_operacion': random.randint(20000, 60000),
                         'recursos_humanos': random.randint(50, 150),
                         'visitas_seguimiento': random.randint(0, 5),
                         'cumplimiento_recomendaciones': random.uniform(70, 100),
                         'seguimiento_enfermedad': random.randint(0, 5),
                         'eventos_adversos': random.randint(0, 2),
                         'reclamaciones_responsabilidad_medica': random.randint(0, 2),
                         'incidentes_seguridad_paciente': random.randint(0, 2),
                         'ensayos_clinicos': random.randint(0, 5),
                         'publicaciones_cientificas': random.randint(0, 3),
                         'descubrimientos_medicos': random.randint(0, 2)})

