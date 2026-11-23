"""Comparación de una malla polar plana con el paraboloide de Flamm.

Ejecutar con::

    poetry run streamlit run streamlit/flamm_paraboloid.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib import cm, colors
import numpy as np
import streamlit as st


st.set_page_config(page_title="Paraboloide de Flamm", layout="wide")
st.title("Plano ecuatorial: espacio plano frente a paraboloide de Flamm")
st.markdown(
    r"""
En un espacio euclídeo tridimensional podemos visualizar directamente un sistema de coordenadas esféricas como una familia de esferas concéntricas.
En el espacio curvo de Schwarzschild, las superficies de simetría siguen siendo esferas, pero las relaciones entre sus distancias no son euclídeas.
Para visualizar esa diferencia geométrica seleccionamos la sección ecuatorial bidimensional, donde las esferas quedan representadas por circunferencias,
y la embebemos en un espacio euclídeo tridimensional mediante el paraboloide de Flamm. Es importante aclarar que el paraboloide no es una imagen literal de un agujero
negro ni de la curvatura del espacio-tiempo en cuatro dimensiones.

En ambos dibujos, $r$ es el **radio circumferencial**: un círculo de radio $r$ tiene
siempre circunferencia $C=2\pi r$.  El panel derecho no representa el
espacio-tiempo completo, sino la geometría espacial de $t=\mathrm{cte}$ y
$\theta=\pi/2$, embebida en un espacio euclídeo auxiliar.

Los círculos con el mismo color tienen la misma circunferencia en ambos paneles.
Para un mismo incremento de radio circumferencial $dr$, la separación radial propia
entre dos círculos aumenta al aproximarse al cuello $r=r_s$:
$d\ell/dr=1/\sqrt{1-r_s/r}$ diverge allí.
"""
)

with st.sidebar:
    st.header("Malla")
    r_max = st.slider(
        r"radio exterior $r/r_s$", min_value=2.2, max_value=16.0, value=8.0, step=0.2
    )
    n_rings = st.slider("círculos de radio", min_value=3, max_value=14, value=7)
    n_rays = st.slider(r"rayos de azimut $\phi$", min_value=4, max_value=24, value=12)
    two_sheets = st.checkbox("mostrar las dos hojas del paraboloide", value=True)
    elev = st.slider("elevación de la vista", min_value=5, max_value=70, value=30)
    azim = st.slider("azimut de la vista", min_value=-180, max_value=180, value=-55)


RS = 1.0  # trabajamos en unidades del radio de Schwarzschild
ring_radii = np.linspace(1.0, r_max, n_rings + 1)[1:]
phi = np.linspace(0.0, 2.0 * np.pi, 361)
ray_radii = np.linspace(1.0, r_max, 300)
circumferences = 2.0 * np.pi * ring_radii
norm = colors.Normalize(vmin=2.0 * np.pi * RS, vmax=2.0 * np.pi * r_max)
# ``matplotlib.cm.get_cmap`` was removed in recent Matplotlib releases.
cmap = plt.get_cmap("viridis")


def flamm_height(radius: np.ndarray) -> np.ndarray:
    """Altura de una hoja del paraboloide de Flamm, en unidades de r_s."""
    return 2.0 * np.sqrt(RS * (radius - RS))


def setup_axis(ax: plt.Axes, title: str) -> None:
    ax.set_title(title, pad=16)
    ax.set_xlabel(r"$x/r_s$")
    ax.set_ylabel(r"$y/r_s$")
    ax.set_zlabel(r"$z/r_s$")
    ax.set_box_aspect((1, 1, 0.48))
    ax.view_init(elev=elev, azim=azim)


fig = plt.figure(figsize=(13.5, 6.2), constrained_layout=True)
flat = fig.add_subplot(1, 2, 1, projection="3d")
flamm = fig.add_subplot(1, 2, 2, projection="3d")
setup_axis(flat, "Espacio euclídeo plano")
setup_axis(flamm, "Espacio de Schwarzschild: paraboloide de Flamm")

# Círculos: el color transmite su circunferencia física, igual en ambos paneles.
for radius, circumference in zip(ring_radii, circumferences, strict=True):
    x = radius * np.cos(phi)
    y = radius * np.sin(phi)
    colour = cmap(norm(circumference))
    flat.plot(x, y, np.zeros_like(phi), color=colour, lw=2.1)
    z = flamm_height(np.full_like(phi, radius))
    flamm.plot(x, y, z, color=colour, lw=2.1)
    if two_sheets:
        flamm.plot(x, y, -z, color=colour, lw=1.2, alpha=0.58)

# Rayos de azimut: sus separaciones radiales muestran el estiramiento cerca de r_s.
for angle in np.linspace(0.0, 2.0 * np.pi, n_rays, endpoint=False):
    x = ray_radii * np.cos(angle)
    y = ray_radii * np.sin(angle)
    flat.plot(x, y, np.zeros_like(ray_radii), color="0.42", lw=0.8, alpha=0.78)
    z = flamm_height(ray_radii)
    flamm.plot(x, y, z, color="0.42", lw=0.8, alpha=0.78)
    if two_sheets:
        flamm.plot(x, y, -z, color="0.42", lw=0.55, alpha=0.45)

# El cuello r=r_s y límites comunes facilitan una comparación honesta de escalas.
neck_x, neck_y = np.cos(phi), np.sin(phi)
for ax, z in ((flat, np.zeros_like(phi)), (flamm, np.zeros_like(phi))):
    ax.plot(neck_x, neck_y, z, color="crimson", lw=2.8, label=r"$r=r_s$")
    ax.set_xlim(-r_max, r_max)
    ax.set_ylim(-r_max, r_max)
    ax.set_zlim(-2.1 * np.sqrt(r_max - 1.0), 2.1 * np.sqrt(r_max - 1.0))

scalar_map = cm.ScalarMappable(norm=norm, cmap=cmap)
scalar_map.set_array(circumferences)
colourbar = fig.colorbar(scalar_map, ax=[flat, flamm], shrink=0.67, pad=0.08)
colourbar.set_label(r"circunferencia $C/r_s = 2\pi r/r_s$")

st.pyplot(fig, use_container_width=True)

proper_radius = (
    np.sqrt(r_max * (r_max - RS))
    + RS * np.log(np.sqrt(r_max) + np.sqrt(r_max - RS))
)
flat_radius = r_max - RS
col1, col2, col3 = st.columns(3)
col1.metric(r"circunferencia exterior", f"{2 * np.pi * r_max:.2f} $r_s$")
col2.metric(r"distancia radial plana desde $r_s$", f"{flat_radius:.2f} $r_s$")
col3.metric(r"distancia radial propia de Schwarzschild", f"{proper_radius:.2f} $r_s$")
