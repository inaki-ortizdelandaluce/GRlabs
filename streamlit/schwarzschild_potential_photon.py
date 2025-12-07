import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Potencial Efectivo para Fotones en Schwarzschild")

st.markdown(
    r"""
Esta aplicación muestra gráficamente el **Potencial Efectivo para fotones**
en el espacio-tiempo de Schwarzschild:
"""
)

st.latex(
    r"V_{\text{eff}}(r) = \frac{1}{r^2}\left(1 - \frac{2GM}{r}\right)"
)

st.markdown(r"""
y permite compararlo con el Potencial Efectivo Newtoniano:
""")
st.latex(
    r"V_{\text{eff, Newton}}(r) = \frac{1}{r^2}"
)

st.markdown(r"""
Graficamos el potencial efectivo en términos de $1/b^2$ (energía efectiva por unidad de masa al cuadrado):
""")
st.latex(
    r"\frac{1}{b^2} = E^2_{\text{eff}}"
)

st.markdown(r"""
**Órbita circular inestable de fotones:** $r = 3GM$, donde $V_{\text{eff}}$ alcanza su máximo con 
$V_{\text{max}} = \frac{1}{27(GM)^2}$, correspondiente a $b_{\text{crit}} = \sqrt{27}\,GM$.

- **$b > \sqrt{27}\,GM$**: Los fotones que vienen del infinito rebotan y regresan al infinito.
- **$b < \sqrt{27}\,GM$**: Los fotones espiralan hacia adentro y caen en el agujero negro.
- **$b = \sqrt{27}\,GM$**: Órbita circular inestable (esfera de fotones).
""")

st.sidebar.header("Parámetros")

# GM
GM = 1.0

# Impact parameter values
b_str = st.sidebar.text_input(
    "Parámetros de impacto $b/GM$ (separados por comas)",
    value=f"{np.sqrt(27):.3f}, 6, 4",
    help=f"Ejemplo: {np.sqrt(27):.3f} (crítico), 6 (rebote), 4 (captura)"
)

show_newtonian = st.sidebar.checkbox("Mostrar potencial newtoniano", value=False)

# X-axis limits
st.sidebar.subheader("Límites del eje X")

r_min = st.sidebar.slider(
    "Min $r/GM$",
    min_value=0.1,
    max_value=5.0,
    value=1.5,
    step=0.1,
)
r_min = r_min * GM

r_max = st.sidebar.slider(
    "Max $r/GM$",
    min_value=5.0,
    max_value=50.0,
    value=15.0,
    step=1.0,
)
r_max = r_max * GM

num_points = 3000

# Y-axis limits
st.sidebar.subheader("Límites del eje Y")
auto_ylim = st.sidebar.checkbox("Escala automática eje Y", value=False)

if not auto_ylim:
    y_min = st.sidebar.slider(
        "Min $1/b^2$",
        min_value=0.0,
        max_value=0.02,
        value=0.0,
        step=0.001,
    )
    y_max = st.sidebar.slider(
        "Max $1/b^2$",
        min_value=0.01,
        max_value=0.1,
        value=0.07,
        step=0.005,
    )

# Parse b values
b_list = []
for part in b_str.split(","):
    part = part.strip()
    if not part:
        continue
    try:
        b_list.append(float(part))
    except ValueError:
        st.sidebar.warning(f"No se pudo interpretar '{part}' como un número; se ignora.")

if not b_list:
    st.error("Por favor ingresa al menos un valor válido para $b$.")
    st.stop()

# --- Physics: define grid and potential ---
r_over_GM = np.linspace(r_min, r_max, num_points)
r = r_over_GM * GM

def V_eff_photon(r, GM):
    """Schwarzschild effective potential for photons"""
    return (1 / r**2) * (1 - 2*GM / r)

def V_eff_newton_photon(r):
    """Newtonian effective potential for photons"""
    return 1 / r**2

# --- Plot ---
fig, ax = plt.subplots(figsize=(12, 7))

# Plot the potential
V_schw = V_eff_photon(r, GM)
ax.plot(r_over_GM, V_schw, label="Potencial de Schwarzschild", linewidth=2.5, color='blue')

if show_newtonian:
    V_newt = V_eff_newton_photon(r)
    ax.plot(r_over_GM, V_newt, label="Potencial Newtoniano", linewidth=2, color='orange')

# Mark the unstable circular orbit at r = 3GM
r_photon_orbit = 3 * GM
if r_min <= r_photon_orbit <= r_max:
    V_max = V_eff_photon(r_photon_orbit, GM)
    ax.plot(r_photon_orbit / GM, V_max, 'ro', markersize=8, label=f"Órbita circular inestable ($r=3GM$)")
    ax.axvline(r_photon_orbit / GM, linestyle='--', linewidth=1.0, color='red', alpha=0.3)

# Mark the event horizon at r = 2GM
r_horizon = 2 * GM
if r_min <= r_horizon <= r_max:
    ax.axvline(r_horizon / GM, linestyle='--', linewidth=1.0, color='black', alpha=0.5)
    ax.text(
        r_horizon / GM, ax.get_ylim()[0] if not auto_ylim else 0,
        "  horizonte ($r=2GM$)",
        va="bottom",
        ha="left",
        fontsize=10
    )

# Plot energy levels for each impact parameter
for b in b_list:
    E_eff = 1 / (b * GM)**2
    # Check if photon will be captured or escape
    b_critical = np.sqrt(27) * GM
    if b * GM < b_critical:
        style = '--'
        label_suffix = " (capturado)"
        color = 'red'
    elif b * GM > b_critical:
        style = '-.'
        label_suffix = " (escapa)"
        color = 'green'
    else:
        style = ':'
        label_suffix = " (crítico)"
        color = 'purple'
    
    ax.axhline(E_eff, linestyle=style, linewidth=1.5, alpha=0.7, color=color,
               label=f"$b/GM={b:.2f}$, $1/b^2={E_eff:.5f}$" + label_suffix)

ax.set_xlabel(r"$r/GM$", fontsize=12)
ax.set_ylabel(r"$1/b^2$ (en unidades de $1/(GM)^2$)", fontsize=12)
ax.set_title("Potencial Efectivo para Fotones en Schwarzschild", fontsize=14)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=9, loc='best')

# Set y-axis limits if not auto scale
if not auto_ylim:
    ax.set_ylim(y_min, y_max)

st.pyplot(fig)

# Display critical information
st.subheader("Información de la Órbita de Fotones")
st.markdown(f"""
- **Radio de la órbita circular inestable:** $r_{{\\text{{fotón}}}} = 3GM$
- **Potencial máximo:** $V_{{\\text{{max}}}} = \\frac{{1}}{{27(GM)^2}} \\approx {1/(27*GM**2):.6f}$
- **Parámetro de impacto crítico:** $b_{{\\text{{crit}}}} = \\sqrt{{27}}\\,GM \\approx {np.sqrt(27)*GM:.3f}\\,GM$
- **Horizonte de eventos:** $r_s = 2GM$
""")

st.markdown("""
### Interpretación física:
- Los fotones con $b > b_{\\text{crit}}$ tienen energía efectiva menor que el máximo del potencial, 
  por lo que son deflectados pero escapan de vuelta al infinito.
- Los fotones con $b < b_{\\text{crit}}$ tienen energía efectiva mayor que el máximo del potencial,
  por lo que pueden superar la barrera y caen inevitablemente en el agujero negro.
- Los fotones con $b = b_{\\text{crit}}$ pueden orbitar en la esfera de fotones en $r = 3GM$,
  pero esta órbita es inestable.
""")
