"""
Generador de datos simulados realistas para el Dashboard Ciudadanía.
Simula datos de contratación en salud del SECOP II enriquecidos con variables exógenas.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# ============================================================
# CONSTANTES Y CATÁLOGOS
# ============================================================

DEPARTAMENTOS = {
    "Amazonas": {"lat": -1.44, "lon": -71.57, "poblacion": 80_000, "idf": 52.1, "itm": 38.5},
    "Antioquia": {"lat": 6.25, "lon": -75.56, "poblacion": 6_900_000, "idf": 78.3, "itm": 72.1},
    "Arauca": {"lat": 7.08, "lon": -70.76, "poblacion": 295_000, "idf": 55.8, "itm": 41.2},
    "Atlántico": {"lat": 10.96, "lon": -74.78, "poblacion": 2_700_000, "idf": 74.6, "itm": 65.3},
    "Bolívar": {"lat": 10.40, "lon": -75.51, "poblacion": 2_200_000, "idf": 58.2, "itm": 45.7},
    "Boyacá": {"lat": 5.53, "lon": -73.36, "poblacion": 1_280_000, "idf": 71.4, "itm": 68.9},
    "Caldas": {"lat": 5.07, "lon": -75.52, "poblacion": 1_000_000, "idf": 72.8, "itm": 70.2},
    "Caquetá": {"lat": 1.61, "lon": -75.61, "poblacion": 510_000, "idf": 48.3, "itm": 35.6},
    "Casanare": {"lat": 5.34, "lon": -72.39, "poblacion": 435_000, "idf": 68.5, "itm": 52.3},
    "Cauca": {"lat": 2.44, "lon": -76.61, "poblacion": 1_470_000, "idf": 53.7, "itm": 42.8},
    "Cesar": {"lat": 10.47, "lon": -73.25, "poblacion": 1_300_000, "idf": 56.1, "itm": 43.5},
    "Chocó": {"lat": 5.69, "lon": -76.66, "poblacion": 550_000, "idf": 35.2, "itm": 28.4},
    "Córdoba": {"lat": 8.75, "lon": -75.88, "poblacion": 1_850_000, "idf": 54.9, "itm": 40.1},
    "Cundinamarca": {"lat": 4.71, "lon": -74.07, "poblacion": 3_200_000, "idf": 82.1, "itm": 76.5},
    "Guainía": {"lat": 3.87, "lon": -67.92, "poblacion": 50_000, "idf": 42.3, "itm": 30.1},
    "Guaviare": {"lat": 2.57, "lon": -72.64, "poblacion": 115_000, "idf": 44.7, "itm": 33.8},
    "Huila": {"lat": 2.93, "lon": -75.28, "poblacion": 1_200_000, "idf": 67.3, "itm": 61.4},
    "La Guajira": {"lat": 11.54, "lon": -72.91, "poblacion": 1_100_000, "idf": 41.8, "itm": 32.6},
    "Magdalena": {"lat": 11.24, "lon": -74.20, "poblacion": 1_400_000, "idf": 49.5, "itm": 38.9},
    "Meta": {"lat": 4.15, "lon": -73.64, "poblacion": 1_060_000, "idf": 69.7, "itm": 58.3},
    "Nariño": {"lat": 1.29, "lon": -77.35, "poblacion": 1_800_000, "idf": 55.4, "itm": 47.2},
    "Norte de Santander": {"lat": 7.89, "lon": -72.49, "poblacion": 1_600_000, "idf": 57.6, "itm": 48.5},
    "Putumayo": {"lat": 1.15, "lon": -76.65, "poblacion": 370_000, "idf": 46.1, "itm": 34.7},
    "Quindío": {"lat": 4.54, "lon": -75.67, "poblacion": 580_000, "idf": 70.2, "itm": 66.8},
    "Risaralda": {"lat": 4.81, "lon": -75.70, "poblacion": 980_000, "idf": 73.5, "itm": 69.1},
    "San Andrés": {"lat": 12.58, "lon": -81.70, "poblacion": 80_000, "idf": 60.3, "itm": 50.2},
    "Santander": {"lat": 7.13, "lon": -73.13, "poblacion": 2_300_000, "idf": 76.8, "itm": 71.6},
    "Sucre": {"lat": 9.30, "lon": -75.39, "poblacion": 950_000, "idf": 50.3, "itm": 37.4},
    "Tolima": {"lat": 4.44, "lon": -75.23, "poblacion": 1_420_000, "idf": 64.5, "itm": 59.7},
    "Valle del Cauca": {"lat": 3.45, "lon": -76.52, "poblacion": 4_800_000, "idf": 77.1, "itm": 73.8},
    "Vaupés": {"lat": 1.19, "lon": -70.17, "poblacion": 45_000, "idf": 38.6, "itm": 27.9},
    "Vichada": {"lat": 4.44, "lon": -69.29, "poblacion": 115_000, "idf": 40.1, "itm": 29.5},
}

TIPOS_ENTIDAD = ["Hospital", "ESE", "IPS", "Secretaría de Salud", "EPS"]

MODALIDADES = [
    "Contratación Directa",
    "Selección Abreviada",
    "Licitación Pública",
    "Mínima Cuantía",
    "Concurso de Méritos",
]

OBJETOS_CONTRATO = [
    "Suministro de medicamentos",
    "Insumos médicos y hospitalarios",
    "Servicios de laboratorio clínico",
    "Mantenimiento equipos biomédicos",
    "Servicios de ambulancia",
    "Alimentación hospitalaria",
    "Aseo y desinfección hospitalaria",
    "Servicios de imagenología",
    "Dotación hospitalaria",
    "Capacitación personal de salud",
    "Servicios de salud domiciliaria",
    "Interventoría contratos de salud",
]

PROVEEDORES = [f"Prov-{str(i).zfill(3)}" for i in range(1, 81)]


# ============================================================
# GENERADOR DE CONTRATOS
# ============================================================

def generar_contratos(n=800):
    """Genera n contratos simulados de salud con distribución realista."""
    
    registros = []
    # Pesos por departamento (más contratos en departamentos grandes)
    deps = list(DEPARTAMENTOS.keys())
    pesos_dep = [DEPARTAMENTOS[d]["poblacion"] for d in deps]
    pesos_dep = np.array(pesos_dep) / sum(pesos_dep)
    
    for i in range(n):
        dep = np.random.choice(deps, p=pesos_dep)
        info_dep = DEPARTAMENTOS[dep]
        
        # Entidad
        tipo_entidad = np.random.choice(TIPOS_ENTIDAD, p=[0.35, 0.30, 0.15, 0.12, 0.08])
        entidad_nombre = f"{tipo_entidad} {dep}"
        nit = f"8{np.random.randint(10000000, 99999999)}"
        
        # Modalidad (sesgo: departamentos con bajo ITM usan más contratación directa)
        if info_dep["itm"] < 45:
            p_mod = [0.50, 0.25, 0.05, 0.15, 0.05]
        else:
            p_mod = [0.25, 0.30, 0.20, 0.15, 0.10]
        modalidad = np.random.choice(MODALIDADES, p=p_mod)
        
        # Fechas
        inicio = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 850))
        duracion_dias = np.random.choice([30, 60, 90, 120, 180, 270, 365],
                                          p=[0.10, 0.15, 0.20, 0.20, 0.15, 0.10, 0.10])
        
        # Valor (distribución log-normal, departamentos pobres con contratos relativamente más altos)
        base = np.random.lognormal(mean=17.5, sigma=1.2)
        if info_dep["idf"] < 50:
            base *= np.random.uniform(1.1, 1.8)  # Inflación en departamentos vulnerables
        valor = round(base, -3)
        valor = max(valor, 5_000_000)  # Mínimo 5M COP
        valor = min(valor, 80_000_000_000)  # Máximo 80B COP
        
        # Proveedor (algunos proveedores dominan)
        if np.random.random() < 0.3:
            proveedor = np.random.choice(PROVEEDORES[:10])  # Top 10 acaparan 30%
        else:
            proveedor = np.random.choice(PROVEEDORES)
        
        # Objeto
        objeto = np.random.choice(OBJETOS_CONTRATO)
        
        # Oferentes
        if modalidad == "Contratación Directa":
            num_oferentes = 1
        elif modalidad == "Mínima Cuantía":
            num_oferentes = np.random.randint(1, 4)
        else:
            num_oferentes = np.random.randint(2, 12)
        
        # Score de riesgo (correlacionado con factores reales)
        score_base = np.random.normal(40, 15)
        if modalidad == "Contratación Directa":
            score_base += 15
        if num_oferentes == 1:
            score_base += 10
        if info_dep["itm"] < 45:
            score_base += 8
        if valor > np.percentile([5_000_000, 80_000_000_000], 90):
            score_base += 12
        # Periodo preelectoral (Oct 2023, Oct 2025)
        mes = inicio.month
        anio = inicio.year
        preelectoral = (anio == 2023 and mes >= 8) or (anio == 2025 and mes >= 8)
        if preelectoral:
            score_base += 7
        # Fin de año fiscal
        if mes >= 11:
            score_base += 5
        
        score = max(5, min(98, round(score_base)))
        
        # Nivel de riesgo
        if score >= 70:
            nivel_riesgo = "Alto"
        elif score >= 45:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Bajo"
        
        # Precio de referencia (para comparar)
        precio_ref = valor * np.random.uniform(0.5, 1.1)
        ratio_precio = valor / precio_ref if precio_ref > 0 else 1.0
        
        registros.append({
            "id_contrato": f"SECOP-{anio}-{str(i+1).zfill(5)}",
            "departamento": dep,
            "lat": info_dep["lat"] + np.random.uniform(-0.5, 0.5),
            "lon": info_dep["lon"] + np.random.uniform(-0.5, 0.5),
            "entidad": entidad_nombre,
            "tipo_entidad": tipo_entidad,
            "nit_entidad": nit,
            "modalidad": modalidad,
            "objeto": objeto,
            "valor": valor,
            "precio_referencia": round(precio_ref, -3),
            "ratio_precio": round(ratio_precio, 2),
            "fecha_publicacion": inicio,
            "duracion_dias": duracion_dias,
            "proveedor": proveedor,
            "num_oferentes": num_oferentes,
            "score_riesgo": score,
            "nivel_riesgo": nivel_riesgo,
            "idf_departamento": info_dep["idf"],
            "itm_departamento": info_dep["itm"],
            "poblacion_departamento": info_dep["poblacion"],
            "periodo_preelectoral": preelectoral,
            "fin_anio_fiscal": mes >= 11,
        })
    
    # Inyectar casos de fragmentación intencional (misma entidad + proveedor + mes)
    fragmentacion_entidades = [
        ("Hospital Bolívar", "Prov-003", "Bolívar", datetime(2024, 3, 5)),
        ("ESE Córdoba", "Prov-007", "Córdoba", datetime(2024, 6, 10)),
        ("Hospital La Guajira", "Prov-002", "La Guajira", datetime(2024, 9, 2)),
        ("ESE Chocó", "Prov-005", "Chocó", datetime(2025, 1, 8)),
        ("Hospital Sucre", "Prov-001", "Sucre", datetime(2024, 11, 15)),
        ("IPS Magdalena", "Prov-004", "Magdalena", datetime(2024, 7, 3)),
    ]
    
    for entidad, proveedor, dep, fecha_base in fragmentacion_entidades:
        info_dep = DEPARTAMENTOS[dep]
        for j in range(np.random.randint(3, 6)):
            fecha = fecha_base + timedelta(days=np.random.randint(0, 25))
            valor = np.random.uniform(20_000_000, 180_000_000)
            precio_ref = valor * np.random.uniform(0.5, 0.9)
            n_total = len(registros)
            registros.append({
                "id_contrato": f"SECOP-{fecha.year}-F{str(n_total).zfill(5)}",
                "departamento": dep,
                "lat": info_dep["lat"] + np.random.uniform(-0.3, 0.3),
                "lon": info_dep["lon"] + np.random.uniform(-0.3, 0.3),
                "entidad": entidad,
                "tipo_entidad": entidad.split()[0],
                "nit_entidad": f"9{np.random.randint(10000000, 99999999)}",
                "modalidad": np.random.choice(["Mínima Cuantía", "Contratación Directa"]),
                "objeto": np.random.choice(OBJETOS_CONTRATO[:4]),
                "valor": round(valor, -3),
                "precio_referencia": round(precio_ref, -3),
                "ratio_precio": round(valor / precio_ref, 2),
                "fecha_publicacion": fecha,
                "duracion_dias": np.random.choice([30, 60, 90]),
                "proveedor": proveedor,
                "num_oferentes": 1,
                "score_riesgo": np.random.randint(55, 90),
                "nivel_riesgo": "Alto" if np.random.random() > 0.3 else "Medio",
                "idf_departamento": info_dep["idf"],
                "itm_departamento": info_dep["itm"],
                "poblacion_departamento": info_dep["poblacion"],
                "periodo_preelectoral": False,
                "fin_anio_fiscal": fecha.month >= 11,
            })
    
    return pd.DataFrame(registros)


def generar_datos_departamento():
    """Genera datos agregados por departamento para scorecard y análisis."""
    
    df = generar_contratos(500)
    
    # Indicadores de salud simulados por departamento (DANE-like)
    indicadores_salud = {}
    for dep, info in DEPARTAMENTOS.items():
        # Correlación inversa: peor desempeño fiscal → peores indicadores de salud
        base_cobertura = 70 + (info["idf"] - 40) * 0.5 + np.random.normal(0, 5)
        base_mortalidad = 25 - (info["idf"] - 40) * 0.2 + np.random.normal(0, 3)
        
        indicadores_salud[dep] = {
            "cobertura_vacunacion": round(max(45, min(98, base_cobertura)), 1),
            "mortalidad_infantil_x1000": round(max(5, min(45, base_mortalidad)), 1),
            "camas_x10000_hab": round(max(3, 8 + (info["idf"] - 50) * 0.1 + np.random.normal(0, 2)), 1),
            "medicos_x10000_hab": round(max(2, 12 + (info["idf"] - 50) * 0.15 + np.random.normal(0, 3)), 1),
        }
    
    df_salud = pd.DataFrame.from_dict(indicadores_salud, orient="index")
    df_salud.index.name = "departamento"
    df_salud = df_salud.reset_index()
    
    return df, df_salud


def calcular_concentracion_proveedores(df):
    """Calcula índice Herfindahl-Hirschman de concentración de proveedores por departamento."""
    
    resultados = []
    for dep, grupo in df.groupby("departamento"):
        total_valor = grupo["valor"].sum()
        if total_valor == 0:
            continue
        shares = grupo.groupby("proveedor")["valor"].sum() / total_valor
        hhi = round((shares ** 2).sum() * 10000)  # HHI escala 0-10000
        top3_share = round(shares.nlargest(3).sum() * 100, 1)
        n_proveedores = grupo["proveedor"].nunique()
        
        resultados.append({
            "departamento": dep,
            "hhi": hhi,
            "top3_concentracion_pct": top3_share,
            "n_proveedores_unicos": n_proveedores,
            "total_contratos": len(grupo),
            "valor_total": total_valor,
        })
    
    return pd.DataFrame(resultados)


def detectar_fragmentacion(df):
    """Detecta posible fragmentación de contratos (misma entidad + proveedor + mes)."""
    
    df_temp = df.copy()
    df_temp["mes"] = df_temp["fecha_publicacion"].dt.to_period("M")
    
    # Agrupar por entidad + proveedor + mes
    grupos = df_temp.groupby(["entidad", "proveedor", "mes"]).agg(
        n_contratos=("id_contrato", "count"),
        valor_total=("valor", "sum"),
        modalidades=("modalidad", lambda x: list(x.unique())),
        objetos=("objeto", lambda x: list(x.unique())),
    ).reset_index()
    
    # Fragmentación = 3+ contratos del mismo proveedor en la misma entidad en el mismo mes
    fragmentados = grupos[grupos["n_contratos"] >= 3].copy()
    fragmentados["mes"] = fragmentados["mes"].astype(str)
    
    return fragmentados.sort_values("valor_total", ascending=False)


# ============================================================
# EXPORTAR DATOS
# ============================================================

if __name__ == "__main__":
    df, df_salud = generar_datos_departamento()
    print(f"Contratos generados: {len(df)}")
    print(f"Departamentos con datos de salud: {len(df_salud)}")
    print(f"Rango de scores: {df['score_riesgo'].min()} - {df['score_riesgo'].max()}")
    print(f"Distribución de riesgo:\n{df['nivel_riesgo'].value_counts()}")
    
    concentracion = calcular_concentracion_proveedores(df)
    print(f"\nConcentración promedio HHI: {concentracion['hhi'].mean():.0f}")
    
    fragmentados = detectar_fragmentacion(df)
    print(f"\nCasos de posible fragmentación: {len(fragmentados)}")
