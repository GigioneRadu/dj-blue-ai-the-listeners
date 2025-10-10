
from ursina import *
import math



class PlanetaSimpla(Entity):

    def __init__(self, nume, a, e, perioada_zile, scara_model, model_file, textura, unghi_initial_grade=0.0):

        # Test de garanție: Folosim modelul 'sphere' implicit (model_file este ignorat)
        super().__init__(
            model = 'sphere',
            scale = scara_model,
            texture = textura,
            collider = 'sphere',
        )

        self.nume = nume
        self.a = a
        self.e = e
        self.perioada_zile = perioada_zile
        self.viteza_unghiulara_medie = (2 * math.pi) / self.perioada_zile
        self.anomalie_medie = math.radians(unghi_initial_grade)
        self.SCALA_UA = 15  #SCALA ORBITALĂ MĂRITĂ LA 15

        self.deseneaza_orbita()
        self.label_nume = Text(
            parent = self,  # Textul este atașat de planetă
            text = self.nume,
            billboard = True,  # Întotdeauna orientat spre cameră
            color = color.white,
            scale = (10 / self.scale_x, 10 / self.scale_y, 10 / self.scale_z),
            # Scalăm invers proporțional cu planeta (pentru a avea aceeași mărime indiferent de planetă)
            y = 1.5,  # Poziționăm textul puțin deasupra planetei
            enabled = False
        )
        self.on_mouse_enter = self.show_name
        self.on_mouse_exit = self.hide_name

    def show_name(self):
        """Activează vizibilitatea label-ului când mouse-ul intră pe collider."""
        self.label_nume.enabled = True

    def hide_name(self):
        """Dezactivează vizibilitatea label-ului când mouse-ul iese de pe collider."""
        self.label_nume.enabled = False

    def _calculeaza_puncte_elipsa(self, num_puncte=100):
        puncte = []
        for i in range(num_puncte + 1):
            theta = (i / num_puncte) * 2 * math.pi
            r = (self.a * (1 - self.e ** 2)) / (1 + self.e * math.cos(theta))
            x = r * math.cos(theta) * self.SCALA_UA
            z = r * math.sin(theta) * self.SCALA_UA
            puncte.append((x, 0.01, z))
        return puncte

    def deseneaza_orbita(self):
        puncte_elipsa = self._calculeaza_puncte_elipsa()
        if puncte_elipsa and puncte_elipsa[0] != puncte_elipsa[-1]:
            puncte_elipsa.append(puncte_elipsa[0])

        self.orbita_vizuala = Entity(
            model=Mesh(vertices=puncte_elipsa, mode='line', static=True),
            color=color.dark_gray.tint(0.5),
            y=0.01,
        )

    def update(self):
        # !!! CORECTIE: VITEZA REDUSĂ DE LA 500 LA 50
        timp_trecut = time.dt * 2
        self.anomalie_medie += self.viteza_unghiulara_medie * timp_trecut

        r = (self.a * (1 - self.e ** 2)) / (1 + self.e * math.cos(self.anomalie_medie))

        unghi_adevarat = self.anomalie_medie
        x = r * math.cos(unghi_adevarat) * self.SCALA_UA
        z = r * math.sin(unghi_adevarat) * self.SCALA_UA

        self.position = (x, 0, z)
        self.rotation_y -= 30 * time.dt

        if self.anomalie_medie > 2 * math.pi:
            self.anomalie_medie -= 2 * math.pi




# -------------------------- APLICAȚIA PRINCIPALĂ --------------------------
app = Ursina()

EditorCamera()
FACTOR_SCALARE_MODEL = 0.2

# 1. SOARELE
soare = Entity(
    model='sphere',
    scale=FACTOR_SCALARE_MODEL * 10,
    texture='sun',
    color=color.yellow
)
PointLight(parent=soare, color=color.white, position=(0, 0, 0))

# 2. PLANETELE
mercur = PlanetaSimpla(
    nume="Mercur", a=0.387, e=0.2056, perioada_zile=88,
    scara_model=FACTOR_SCALARE_MODEL * 0.35,
    model_file='Mercur', textura='mercur', unghi_initial_grade=0
)

venus = PlanetaSimpla(
    nume="Venus", a=0.723, e=0.08, perioada_zile=225,
    scara_model=FACTOR_SCALARE_MODEL * 0.87,
    model_file='Venus', textura='venus', unghi_initial_grade=45
)

pamant = PlanetaSimpla(
    nume="Pământ", a=1.0, e=0.0167, perioada_zile=365,
    scara_model=FACTOR_SCALARE_MODEL * 0.91,
    model_file='Earth', textura='earth', unghi_initial_grade=90
)
marte = PlanetaSimpla(
    nume="Marte", a=1.524, e=0.0934, perioada_zile=687,
    scara_model=FACTOR_SCALARE_MODEL * 0.91,
    model_file='Marte', textura='mars', unghi_initial_grade=135
)
jupiter = PlanetaSimpla(
    nume="Jupiter", a=5.204, e=0.048, perioada_zile=4332,
    scara_model=0.91,
    model_file='Jupiter', textura='jupiter', unghi_initial_grade=120,
)
saturn = PlanetaSimpla(
    nume="Saturn", a=9.582, e=0.056, perioada_zile=10759,
    scara_model=1.0, # Am mărit puțin scara lui Saturn la 1.0 (de la 0.75)
    model_file='Saturn', textura='saturn', unghi_initial_grade=150
)

uranus = PlanetaSimpla(
    nume="Uranus", a=19.201, e=0.047, perioada_zile=30687,
    scara_model=1,
    model_file='Uranus', textura='uranus', unghi_initial_grade=180,
)
neptun = PlanetaSimpla(
    nume="Neptun", a=30.047, e=0.009, perioada_zile=60190,
    scara_model=1.5,
    model_file="Neptun", textura='neptun', unghi_initial_grade=210,
)

# 3. FUNDAL ȘI CAMERĂ
Sky(texture='galaxi_sky1')


camera.position = (0, 7, -40)
camera.rotation = (13, 0, 0)

app.run()