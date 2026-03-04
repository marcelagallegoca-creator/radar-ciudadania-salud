# 🏥 Radar Ciudadano — Contratación en Salud (SECOP)

Dashboard interactivo de vigilancia ciudadana para la contratación pública en el sector salud colombiano.

## Descripción

Prototipo académico que utiliza datos simulados realistas para demostrar cómo la ciudadanía puede monitorear la contratación pública en salud, detectar señales de atipicidad y ejercer control social informado.

**Proyecto:** Sistema de Alertas Tempranas para Contratación en Salud (SATCS) — "Alerta Salud Abierta"  
**Programa:** Especialización en Inteligencia Artificial — Universidad Javeriana  
**Metodología:** Design Thinking — Fase 5: Testear (Dashboard Visión Ciudadanía)

## Módulos

| # | Módulo | Descripción |
|---|--------|-------------|
| 1 | **Scorecard departamental** | Resumen ejecutivo por departamento: contratos, alertas, indicadores fiscales y de salud, ranking nacional |
| 2 | **Contratos atípicos** | Top contratos con mayor score de riesgo, con explicación en lenguaje ciudadano y posibles explicaciones legítimas |
| 3 | **Concentración de proveedores** | Índice Herfindahl-Hirschman por departamento: ¿pocos proveedores acaparan la contratación? |
| 4 | **Gasto vs. Resultados** | Scatter plot cruzando gasto per cápita en salud con indicadores DANE (cobertura, mortalidad, camas, médicos) |
| 5 | **Precios de referencia** | Comparación del valor pagado vs. precio de referencia para contratos similares |
| 6 | **Fragmentación de contratos** | Detección de posible fraccionamiento: misma entidad + proveedor + mes con múltiples contratos |

## Variables exógenas integradas

- **Índice de Desempeño Fiscal (IDF)** — DNP
- **Índice de Transparencia Municipal (ITM)** — Transparencia por Colombia
- **Indicadores de salud** — DANE / TerriData (cobertura vacunación, mortalidad infantil, camas y médicos por habitante)
- **Calendario electoral** — Periodos preelectorales
- **Fin de año fiscal** — Presión por ejecución presupuestal

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/[tu-usuario]/radar-ciudadania-salud.git
cd radar-ciudadania-salud

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

## Estructura del proyecto

```
radar-ciudadania/
├── app.py                 # Dashboard principal (Streamlit)
├── data_generator.py      # Generador de datos simulados realistas
├── requirements.txt       # Dependencias Python
├── .gitignore
└── README.md
```

## Datos

Este prototipo trabaja con **datos simulados realistas** que replican la estructura y distribución de datos del SECOP II. Para una implementación real, el módulo `data_generator.py` debería reemplazarse por un conector a la API de SECOP II (Socrata/Sodapy).

## Consideraciones éticas

- El dashboard identifica **patrones estadísticos atípicos**, no irregularidades confirmadas
- Cada alerta incluye explicación de **posibles razones legítimas**
- No se muestran nombres de personas naturales
- Se incluye **indicador de fiabilidad** de los datos por departamento
- El disclaimer es permanente y visible

## Licencia

Proyecto académico. Uso libre con atribución.
