import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Potencial Efectivo de Schwarzschild")

st.markdown(
    r"""
Esta aplicación muestra gráficamente el **Potencial Efectivo por unidad de masa** para una partícula de prueba
en el espacio-tiempo de Schwarzschild:
"""
)

st.latex(
    r"V_{\text{eff}}(r) = -\frac{GM}{r} + \frac{\ell^2}{2 r^2} - \frac{GM\,\ell^2}{r^3}"
)

st.markdown(r"""
            y permite compararlo con el Potencial Efectivo por unidad de masa Newtoniano:
""")
st.latex(
    r"V_{\text{eff, Newton}}(r) = -\frac{GM}{r} + \frac{\ell^2}{2 r^2}" 
)

# --- Sidebar controls ---
st.sidebar.header("Parámetros")

# GM value
GM = 1.0

# l values
lambda_str = st.sidebar.text_input(
    "$\ell$/GM",
    value="4",
    help="Ejemplo: 3.464 (ISCO - inflexión), 4, 5, 7 (órbitas estables con mín/máx)"
)

# Show Newtonian comparison
show_newtonian = st.sidebar.checkbox("Potencial Newtoniano", value=False)

# X-axis limits
st.sidebar.subheader("Límites del eje X")

r_min = st.sidebar.slider(
    "Min $r/GM$",
    min_value=0.01,
    max_value=10.0,
    value=2.5,
    step=0.1,
)
r_min = r_min * GM

r_max = st.sidebar.slider(
    "Max $r/GM$",
    min_value=10.0,
    max_value=1000.0,
    value=500.0,
    step=10.0,
)
r_max = r_max * GM

num_points = 3000
# Number of points for the radial grid
#num_points = st.sidebar.slider(
#    "Número de puntos",
#    min_value=200,
#    max_value=3000,
#    value=1000,
#    step=100,
#)

# Y-axis limits
st.sidebar.subheader("Límites del eje Y")
auto_ylim = st.sidebar.checkbox("Escala automática eje Y", value=False)

if not auto_ylim:
    y_min = st.sidebar.slider(
        "Min $V_{\\text{eff}}$",
        min_value=-1.0,
        max_value=0.5,
        value=-0.05,
        step=0.01,
    )
    y_max = st.sidebar.slider(
        "Max $V_{\\text{eff}}$",
        min_value=-0.5,
        max_value=1.0,
        value=0.02,
        step=0.01,
    )


# Parse l values
l_list = []
for part in lambda_str.split(","):
    part = part.strip()
    if not part:
        continue
    try:
        l_list.append(float(part))
    except ValueError:
        st.sidebar.warning(f"No se pudo interpretar '{part}' como un número; se ignora.")

if not l_list:
    st.error("Por favor ingresa al menos un valor válido para $\ell$.")
    st.stop()

# --- Physics: define grid and potential ---
r_over_GM = np.linspace(r_min, r_max, num_points)
r = r_over_GM * GM

def V_eff(r, GM, l):
    return (
        -GM / r
        + 0.5 * (l**2) / (r**2)
        - GM * (l**2) / (r**3)
    )

def V_eff_newton(r, GM, l):
    """Newtonian effective potential (without 1/r^3 term)"""
    return (
        -GM / r
        + 0.5 * (l**2) / (r**2)
    )

# --- Plot ---
fig, ax = plt.subplots(figsize=(12, 7))

# Store info about extrema
extrema_info = []

for l in l_list:
    V = V_eff(r, GM, l)
    ax.plot(r_over_GM, V, label=rf"$\ell = {l:.3g}$ (Schwarzschild)", linewidth=2)
    
    # Plot Newtonian comparison if requested
    if show_newtonian:
        V_newton = V_eff_newton(r, GM, l)
        ax.plot(r_over_GM, V_newton, linewidth=2, 
                label=rf"$\ell = {l:.3g}$ (Newton)")
    
    # Calculate and mark extrema if l > 2*sqrt(3)*GM
    l_critical = 2 * np.sqrt(3) * GM
    if l > l_critical:
        discriminant = 1 - 12 * (GM / l)**2
        if discriminant > 0:
            sqrt_disc = np.sqrt(discriminant)
            r_max_loc = 6 * GM / (1 + sqrt_disc)
            r_min_loc = 6 * GM / (1 - sqrt_disc)
            
            if r_min <= r_max_loc <= r_max:
                V_max = V_eff(r_max_loc, GM, l)
                ax.plot(r_max_loc / GM, V_max, 'ro', markersize=6)
                extrema_info.append(f"$\ell/GM={l:.3g}$: max en $r/GM={r_max_loc / GM:.3f}$")
            
            if r_min <= r_min_loc <= r_max:
                V_min = V_eff(r_min_loc, GM, l)
                ax.plot(r_min_loc / GM, V_min, 'go', markersize=6)
                extrema_info.append(f"$\ell/GM={l:.3g}$: min en $r/GM={r_min_loc / GM:.3f}$")

# Mark the horizon at r = 2GM (r/GM = 2)
r_s = 2 * GM
if r_min <= r_s <= r_max:
    ax.axvline(2, linestyle="--", linewidth=1.0, color='black', alpha=0.5)
    ax.text(
        2, ax.get_ylim()[0],
        "  horizonte ($r/GM=2$)",
        va="bottom",
        ha="left",
    )

ax.set_xlabel(r"$r/GM$", fontsize=12)
ax.set_ylabel(r"$V_\text{eff}$ (por unidad de masa)", fontsize=12)
ax.set_title("Potencial Efectivo de Schwarzschild", fontsize=14)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

# Set y-axis limits if not auto scale
if not auto_ylim:
    ax.set_ylim(y_min, y_max)

st.pyplot(fig)

# Display extrema info
if extrema_info:
    st.subheader("Puntos Críticos")
    st.markdown("**Puntos rojos:** Máximos locales (órbitas inestables)")
    st.markdown("**Puntos verdes:** Mínimos locales (órbitas estables)")
    for info in extrema_info:
        st.markdown(f"- {info}")
