from pathlib import Path
import json, math, re, html
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
SNAP=json.loads((ROOT/'docs/evidence/model_snapshot_2026-10-25.json').read_text(encoding='utf-8'))
for name,file in [('Nexo','arial.ttf'),('NexoBold','arialbd.ttf'),('NexoItalic','ariali.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Nexo',normal='Nexo',bold='NexoBold',italic='NexoItalic',boldItalic='NexoBold')
INK=colors.HexColor('#17212B'); ORANGE=colors.HexColor('#F4773D'); MUTED=colors.HexColor('#526271'); EDGE=colors.HexColor('#DADFE3'); LIGHT=colors.HexColor('#F3F5F6')
W,H=A4; WIDTH=W-100
ST={
 'body':ParagraphStyle('Body',fontName='Nexo',fontSize=10.2,leading=15,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('Small',fontName='Nexo',fontSize=8.3,leading=11.5,textColor=MUTED,spaceAfter=6),
 'h1':ParagraphStyle('H1',fontName='NexoBold',fontSize=25,leading=29,textColor=INK,spaceAfter=17),
 'h2':ParagraphStyle('H2',fontName='NexoBold',fontSize=12.3,leading=17,textColor=INK,spaceBefore=10,spaceAfter=7),
 'eyebrow':ParagraphStyle('Eye',fontName='NexoBold',fontSize=8.5,leading=12,textColor=colors.HexColor('#B4461C'),spaceAfter=9),
 'cell':ParagraphStyle('Cell',fontName='Nexo',fontSize=8.7,leading=12,textColor=INK),
 'th':ParagraphStyle('TH',fontName='NexoBold',fontSize=8.5,leading=11.5,textColor=colors.white),
 'formula':ParagraphStyle('Formula',fontName='Mono',fontSize=10,leading=15,textColor=INK,spaceAfter=0),
 'quote':ParagraphStyle('Quote',fontName='NexoItalic',fontSize=11.2,leading=17,textColor=INK,spaceAfter=8),
}

def clean(s):
    return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u2212','-')
def p(s,style='body'):return Paragraph(clean(s),ST[style])
def sub(s):return p(s,'h2')
def table(head,rows,widths=None):
    widths=widths or [WIDTH/len(head)]*len(head)
    data=[[p(html.escape(str(x)),'th') for x in head]]+[[p(html.escape(clean(x)),'cell') for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,0),2,ORANGE),('LINEBELOW',(0,1),(-1,-1),.4,EDGE)]))
    return t
def box(text,formula=False):
    t=Table([[p(text,'formula' if formula else 'body')]],colWidths=[WIDTH])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.6,EDGE),('LINEBEFORE',(0,0),(0,-1),3,ORANGE),('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
    return t

class Flow(Flowable):
    def __init__(self,labels):Flowable.__init__(self);self.labels=labels;self.width=WIDTH;self.height=63
    def draw(self):
        c=self.canv;n=len(self.labels);gap=14;bw=(WIDTH-gap*(n-1))/n
        for i,label in enumerate(self.labels):
            x=i*(bw+gap);c.setFillColor(LIGHT);c.setStrokeColor(EDGE);c.roundRect(x,8,bw,46,6,fill=1,stroke=1)
            parts=label.split('|');c.setFillColor(INK);c.setFont('NexoBold',8.2)
            for j,line in enumerate(parts):c.drawCentredString(x+bw/2,34-j*12,clean(line))
            if i<n-1:
                c.setStrokeColor(ORANGE);c.line(x+bw+2,31,x+bw+gap-3,31);c.line(x+bw+gap-6,34,x+bw+gap-3,31);c.line(x+bw+gap-6,28,x+bw+gap-3,31)

def footer(label):
    def draw(c,doc):
        c.saveState();c.setStrokeColor(EDGE);c.line(50,H-43,W-50,H-43);c.setFont('NexoBold',8);c.setFillColor(INK);c.drawString(50,H-31,'NEXO');c.setFont('Nexo',8);c.setFillColor(MUTED);c.drawRightString(W-50,H-31,label)
        c.line(50,43,W-50,43);c.setFont('Nexo',7.4);c.drawString(50,29,'Documentación académica | Corte: 25 de octubre de 2026 | Hermosillo, UTC-7');c.drawRightString(W-50,29,str(doc.page));c.restoreState()
    return draw

def cover(title,subtitle,tag):
    return [Spacer(1,65),p('NEXO / FÚTBOL CON EVIDENCIA','eyebrow'),Spacer(1,18),p(title,'h1'),p(subtitle,'quote'),Spacer(1,27),Flow(['Datos|reales','Modelos|estadísticos','Validación|temporal']),Spacer(1,23),box('Poisson + regresión lineal OLS + CatBoost'),Spacer(1,25),p(tag),p('Versión documentada: specialists-v2.0 + linear-ols-v1. Estado de modelos consultado en la base local el 25 de octubre de 2026.','small'),p('Documento basado en la implementación actual. No reproduce credenciales, claves de API ni datos privados. Las cifras del estado de aprendizaje corresponden a una instantánea; pueden cambiar con nuevas ingestas.','small')]

def page(story,n,title,items):
    story.append(PageBreak());story.extend([p(f'{n:02d} / DOCUMENTACIÓN DEL PROYECTO','eyebrow'),p(title,'h1')]);story.extend(items)

def emit(name,story,label):
    doc=SimpleDocTemplate(str(OUT/name),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=61,bottomMargin=60,title=label,author='Nexo - documentación del proyecto',subject='KDD, aprendizaje supervisado y análisis de fútbol')
    doc.build(story,onFirstPage=footer(label),onLaterPages=footer(label))
    r=PdfReader(OUT/name);print(name,len(r.pages),'páginas')

names={'result':'Ganador / empate','goals':'Goles','corners':'Córners','yellows':'Amarillas'}
def modelrows():
    return [[names[r['market']], 'Previo' if r['phase']=='PRE' else 'En vivo',r['active'],str(r['report'].get('samples',0))] for r in SNAP]
def linearrows():
    result=[]
    for r in SNAP:
        if r['phase']!='PRE' or not r.get('linear'):continue
        v=r['linear'];result.append([names[r['market']],{'adopted':'Adoptada','not_improved':'No mejoró','awaiting_fresh_test':'Espera prueba nueva'}.get(v['status'],v['status']),f"{v['candidate']['mae']:.3f}" if 'candidate' in v else '-',f"{v['baseline']['mae']:.3f}" if 'baseline' in v else '-'])
    return result

full=cover('Documentación\ncompleta'.replace('\n','<br/>'),'Arquitectura, datos, predicción, aprendizaje, evaluación, seguridad y operación.','Proyecto académico para Extracción de Conocimiento en Bases de Datos. Guía técnica y funcional de la aplicación existente.')
page(full,1,'Propósito y alcance',[
 p('<b>Nexo</b> centraliza información de fútbol, calcula probabilidades y registra selecciones simuladas para contrastarlas con resultados confirmados. Su valor académico es hacer trazable el recorrido desde los datos hasta la evaluación.'),
 sub('Objetivos'),p('Consultar encuentros y estadísticas reales; transformar historiales en variables; comparar especialistas por mercado y fase; medir sus errores; conservar versiones y presentar la información de manera accesible.'),
 sub('Lectura del documento'),table(['Bloque','Contenido'],[['Sistema','Arquitectura, proveedores y persistencia.'],['Conocimiento','KDD, variables y calidad de datos.'],['Predicción','Poisson, OLS, CatBoost, combinación y fase en vivo.'],['Evaluación','Validación temporal, métricas y estado consultado.'],['Operación','Momios, selecciones, interfaz, seguridad, PWA, API y ejecución.']],[105,WIDTH-105]),
 sub('Lo que significa un pronóstico'),p('Es una estimación condicionada por datos y supuestos. Un porcentaje alto no convierte el resultado en seguro. Las apuestas del proyecto son simulaciones sin dinero, independientes del marcador real y de la animación de la cancha.'),
 box('<b>Alcance verificado:</b> existen especialistas entrenados de regresión lineal y CatBoost. No todos están activos para todos los mercados. La cobertura de estadísticas y canchas depende del proveedor.'),
])
page(full,2,'Arquitectura del sistema',[
 Flow(['React|Interfaz','FastAPI|Servicios','SQLAlchemy|Persistencia','APIs|Proveedores']),
 p('El frontend es una SPA con React, Vite y Tailwind CSS. FastAPI expone servicios HTTP y Python ejecuta ingesta, análisis y entrenamiento. SQLAlchemy conecta las entidades con PostgreSQL o SQLite; el arranque local admite SQLite cuando no hay PostgreSQL disponible.'),
 table(['Capa','Responsabilidad','Ubicación'],[['Presentación','Rutas, filtros, formularios y gráficos.','frontend/src'],['API','Validación de entradas y acceso a servicios.','backend/app/api/v1'],['Servicios','Ingesta, modelos, selecciones y evaluación.','backend/app/services'],['Modelo y dominio','Proyecciones estadísticas e identidad.','backend/app/ml y domain'],['Infraestructura','Tablas, sesiones, caché y adaptadores.','backend/app/infrastructure']],[83,217,WIDTH-300]),
 sub('Flujo de consulta'),p('El navegador solicita datos a /api/v1. El backend devuelve información persistida y su estado de actualización. Los procesos programados consultan proveedores para reducir duplicación de solicitudes. Excepción visual: SportScore se incrusta como iframe externo, por lo que el navegador sí se conecta a ese proveedor para la cancha.'),
 sub('Trabajos periódicos'),p('Resultados: aproximadamente cada 60 segundos. Calendario amplio: cada tres horas. Plantillas y momios: trabajos de 24 horas. Entrenamiento de especialistas: cada seis horas. También hay tareas iniciales al arrancar. Un trabajo puede no ejecutarse si otro mantiene el bloqueo de ingesta.'),
 p('El scheduler y los bloqueos actuales están pensados para un único proceso local. Escalar a varios workers requiere coordinación compartida y separar los trabajos de la API.','small'),
])
page(full,3,'Fuentes y calidad de datos',[
 table(['Fuente','Uso actual','Límite relevante'],[['ESPN público','Calendarios, marcadores, equipos, plantillas y estadísticas disponibles.','Sin contrato de latencia ni disponibilidad; cobertura variable.'],['The Odds API','Momios previos de referencia cuando hay coincidencia y cuota válida.','Clave privada, cuota de solicitudes y caché; no es un feed de momios en vivo.'],['SportScore','Cancha de un encuentro explícitamente vinculado.','Solo visualización; no alimenta el entrenamiento.']],[100,219,WIDTH-319]),
 sub('Reglas de integridad'),p('Los identificadores de cada proveedor no se intercambian. Se revisan identidad de equipos, competición, fecha y hora. Los resultados deben ser finalizados y verificados para incorporarse como etiquetas. Se descartan duplicados del mismo evento y ejemplos incompatibles con el alcance a 90 minutos.'),
 p('Un dato ausente se conserva como ausente; no se considera cero. Para córners y amarillas el motor exige historial observado suficiente de ambos equipos y, en vivo, contadores recientes. Cuando no se cumplen las condiciones, el mercado se omite o se informa como no disponible.'),
 sub('Imputación técnica, distinta de inventar estadísticas'),p('OLS puede reemplazar una entrada numérica faltante por la mediana calculada solo en entrenamiento; excluye columnas sin observaciones. Es un tratamiento interno explícito del modelo, no una estadística real mostrada del equipo. No reemplaza la elegibilidad del historial ni crea resultados finales.'),
 sub('Competiciones configuradas'),p('Liga MX (MX), Premier League (PL), La Liga (PD), Serie A (SA), MLS, Champions League (CL), Bundesliga (BL1) y Saudi Pro League (SPL). La configuración permite consultarlas; no garantiza cobertura idéntica en cada proveedor.'),
])
page(full,4,'Persistencia y trazabilidad',[
 p('La base conserva hechos deportivos, agregados y decisiones del sistema. Esto permite reconstruir qué información estaba disponible al emitir un pronóstico y qué versión se utilizó.'),
 table(['Entidad o grupo','Función'],[['League, Team y Player','Competiciones, equipos, identidad y plantillas.'],['Match','Encuentro, proveedor, fecha, estado, marcador y detalles recibidos.'],['CountObservation','Contadores observados de córners y amarillas.'],['TeamFormSnapshot y Prediction','Forma agregada y predicción deportiva serializada.'],['ForecastSnapshot','Captura de un pronóstico previo o en vivo con sus parámetros.'],['ForecastSelection y vínculos automáticos','Selección simulada, estado, revisiones y liquidación.'],['MarketLearner y ForecastRevision','Modelos entrenados, informes y revisiones de calibración.'],['ShadowForecast','Capturas experimentales de candidatos CatBoost.'],['OddsObservation, caché y FeedState','Capturas de cuotas, reutilización de respuestas y estado de fuentes.'],['User y LoginAttempt','Acceso a cuentas y control de intentos.']],[190,WIDTH-190]),
 sub('Separación de responsabilidades'),p('Un resultado real no se modifica para coincidir con un pronóstico. Una captura de cuotas conserva la hora de captura. La selección guarda el modelo y la política usados. Las revisiones futuras no borran el registro de decisiones ya iniciadas.'),
 p('Existen tablas y rutas heredadas de versiones anteriores. La arquitectura descrita aquí se basa en specialists-v2.0 y linear-ols-v1, no en las fórmulas históricas que aún aparecen en algunos documentos antiguos.','small'),
])
page(full,5,'Proceso KDD y variables',[
 Flow(['Seleccionar|datos','Limpiar|y validar','Transformar|variables','Modelar|y evaluar']),
 table(['Etapa KDD','Aplicación'],[['Selección','Encuentros de proveedores admitidos y resultados verificables.'],['Limpieza','Identidad, fechas, valores válidos, duplicados y cobertura.'],['Transformación','Ventanas históricas y vector numérico/categórico.'],['Minería','Poisson como base, regresión lineal OLS y CatBoost.'],['Interpretación','Métricas, estados, informes y comparación con resultados.']],[108,WIDTH-108]),
 sub('Entradas de los especialistas'),p('La liga es una categoría. Las variables numéricas incluyen goles a favor y en contra, puntos, descanso y proporción de antecedentes como local para cada equipo. Córners y amarillas agregan promedios de conteos a favor y en contra. En vivo se añaden minuto, goles de ambos equipos y contador observado.'),
 sub('Ventana histórica'),p('El motor reconstruye los últimos cinco antecedentes elegibles por equipo dentro del intervalo histórico admitido. Excluye el propio evento, partidos posteriores y antecedentes demasiado cercanos. Algunos antecedentes publicados en resúmenes pueden pertenecer a otras competiciones; eso amplía cobertura, pero no ajusta automáticamente la fuerza entre ligas.'),
 box('<b>Etiqueta supervisada:</b> resultado 0/1/2 para local/empate/visitante; total final para conteos previos; conteo restante desde la captura para modelos en vivo. El resultado futuro no forma parte de las entradas previas.'),
])
poisson_example=1-math.exp(-2.8)*(1+2.8+2.8**2/2)
page(full,6,'Poisson: cantidades y probabilidades',[
 p('Poisson es una distribución discreta para representar cantidades de eventos. El parámetro lambda es la cantidad esperada, que se estima a partir del historial o de un especialista entrenado. No es un conteo observado.'),
 box('P(X = k) = exp(-lambda) * lambda^k / k!',True),
 p('k es una cantidad entera no negativa. En la base de goles, la tasa del local combina su promedio ofensivo con los goles recibidos del visitante, y viceversa. La suma de las tasas aproxima el total esperado.'),
 sub('Ganador o empate'),p('La base construye probabilidades de marcadores combinando las distribuciones de ambos equipos. Se suman las celdas donde el local anota más, ambos anotan igual o el visitante anota más. CatBoost puede producir el vector 1X2 directamente y combinarlo con esta base.'),
 sub('Más / menos'),box('Más de 2.5 goles = P(X >= 3) = 1 - P(0) - P(1) - P(2)',True),
 p(f'<b>Ejemplo didáctico:</b> con lambda = 2.8, la probabilidad Poisson de tres goles o más es aproximadamente {poisson_example*100:.1f}%. No es un pronóstico de un partido real.'),
 sub('Supuestos y límites'),p('Una Poisson simple vincula media y varianza. El fútbol puede presentar dependencia entre eventos, cambios de ritmo y dispersión distinta, especialmente en córners y tarjetas. Por eso se mide el error de la distribución y no se supone que una tasa histórica sea una ley del partido.'),
 p('Implementación principal: backend/app/ml/markets.py y market_pipeline.py. La proyección de mercados puede incorporar parámetros de calibración; la fórmula anterior explica la distribución base.','small'),
])
page(full,7,'Regresión lineal OLS',[
 p('Está implementada y entrenada mediante sklearn.linear_model.LinearRegression. OLS ajusta coeficientes para reducir la suma de errores cuadrados. Se aplica a goles, córners y amarillas, con modelos independientes en previo y en vivo; no se aplica directamente al vector de probabilidades 1X2.'),
 box('y_estimado = b0 + b1*z1 + b2*z2 + ... + bn*zn',True),
 p('Las z son variables transformadas. Las ligas se codifican como categorías indicadoras. Para columnas numéricas observadas se guardan mediana y escala aprendidas en entrenamiento. Las columnas sin datos de entrenamiento se excluyen. Esas transformaciones se reutilizan en validación, prueba e inferencia.'),
 sub('Qué predice y cómo se utiliza'),p('El valor estimado representa una tasa de conteo: total en previo o cantidad restante en vivo. Como una recta puede producir negativos, se aplica un límite inferior de 0.01. Después la tasa pasa a la proyección Poisson para convertirla en probabilidades de más/menos.'),
 box('<b>Ejemplo inventado solo para explicar la fórmula:</b><br/>goles estimados = 0.8 + 0.6 x promedio ofensivo + 0.4 x promedio recibido rival.<br/>Con 2.0 y 1.5: 0.8 + 1.2 + 0.6 = 2.6. Estos coeficientes no son los del modelo guardado.'),
 sub('Ventajas y precauciones'),p('Es una referencia interpretable y económica. Supone una relación aditiva lineal; no descubre por sí sola interacciones complejas. La codificación completa de ligas junto con intercepto puede hacer que los coeficientes no sean únicos, aunque la solución por mínimos cuadrados produzca predicciones utilizables. Los coeficientes no prueban causalidad.'),
 p('Los modelos se guardan como JSON con coeficientes, intercepto y transformaciones bajo linear-ols-v1. Archivo: backend/app/services/linear_models.py.','small'),
])
page(full,8,'CatBoost: árboles que se combinan',[
 p('CatBoost es aprendizaje supervisado mediante gradient boosting de árboles de decisión. Construye árboles sucesivos para reducir una función de pérdida. No es un solo árbol ni una regresión lineal.'),
 Flow(['Variables|del partido','Árbol 1|aporte','Árbol 2|corrección','Conjunto|predicción']),
 sub('Clasificación y regresión'),table(['Uso','Implementación','Salida'],[['Ganador / empate','CatBoostClassifier; pérdida MultiClass.','Probabilidades local, empate y visitante.'],['Goles, córners y amarillas','CatBoostRegressor; pérdida Poisson.','Tasa positiva estimada de conteo.']],[125,212,WIDTH-337]),
 sub('Configuración del proyecto'),p('Cada mercado y fase usa su propio modelo. Configuración registrada: 160 iteraciones, profundidad 4, learning_rate 0.04, regularización L2 de 8, semilla 42 y dos hilos. La liga se declara variable categórica. El orden temporal se conserva con has_time=True.'),
 sub('Cómo interpretar los árboles'),p('Un árbol puede separar ejemplos por promedios ofensivos o descanso; las preguntas y umbrales se aprenden, no se escriben manualmente. La suma de aportes representa relaciones no lineales. El informe guarda importancia de variables, que describe el modelo pero no demuestra causalidad.'),
 box('<b>Distinción fundamental:</b> CatBoostRegressor es regresión basada en árboles. LinearRegression es regresión lineal OLS. El proyecto contiene ambas técnicas y las compara, sin confundir sus nombres.'),
])
page(full,9,'Combinación y análisis en vivo',[
 table(['Momento','Información permitida','Objetivo'],[['Previo','Historial anterior al inicio y cuotas previas válidas.','Distribución del resultado final.'],['En vivo','Historial, minuto, marcador y contadores recientes.','Resultado final o cantidad que falta por ocurrir.']],[80,250,WIDTH-330]),
 sub('Combinación deportiva'),box('salida = (1 - w) * base_Poisson + w * especialista',True),
 p('El peso w se elige entre 0, 0.25, 0.5, 0.75 y 1 mediante validación. Puede combinarse un vector de probabilidades 1X2 o una tasa de conteo. El motor no suma OLS, CatBoost y Poisson con pesos arbitrarios: un especialista candidato debe superar al modelo activo.'),
 sub('Partido en curso'),p('Para goles se reduce la tasa base al tiempo restante usando un horizonte de 95 minutos. Un especialista en vivo puede estimar esa cantidad restante con variables del minuto y marcador. Los eventos ya ocurridos se conservan como contador actual, no se vuelven a pronosticar como si aún no hubieran sucedido.'),
 p('Si el marcador está pendiente de confirmación, no hay minuto utilizable, falta contador reciente o la información envejece más allá del límite, el sistema puede suspender el pronóstico en vivo. Los especialistas en vivo no heredan automáticamente el entrenamiento de los previos.'),
 sub('Coherencia y límites'),p('Ganador y goles tienen objetivos independientes: sus salidas no garantizan una única distribución conjunta perfectamente coherente. No se incluyen prórroga ni penales en el alcance declarado. El horizonte de 95 minutos es una aproximación, no una duración observada del encuentro.'),
])
page(full,10,'Aprendizaje y validación temporal',[
 p('El aprendizaje se realiza por lotes con resultados confirmados. Recibir una actualización no equivale a reentrenar ni a adoptar un modelo. El scheduler revisa especialistas cada seis horas; un mismo conjunto de datos se identifica con una huella para evitar repetirlo sin necesidad.'),
 Flow(['60%|Entrenar','20%|Validar peso','20%|Probar','Comparar|y decidir']),
 p('Se exigen al menos 200 ejemplos; además, los bloques deben contener al menos 100 ejemplos de entrenamiento y 30 por cada bloque posterior. Los cortes respetan fechas y separaciones de tres horas. Un evento no debe aparecer simultáneamente en entrenamiento y prueba; las capturas en vivo se reducen a un ejemplo por encuentro elegible.'),
 sub('Condiciones de adopción'),p('El candidato debe tener peso mayor que cero y reducir el log loss de prueba en más de 0.002 frente a la base y al modelo vigente. CatBoost exige datos para las tres clases en entrenamiento. Si no hay mejora o falta evidencia, se conserva el modelo anterior.'),
 sub('Qué tan independiente es la prueba'),p('La primera comparación de OLS es un benchmark histórico cronológico compartido con otros especialistas. No constituye evidencia prospectiva completamente inédita de todo el sistema. Las siguientes revisiones de una familia necesitan un bloque posterior al ya usado; aun así, la selección reiterada entre familias debe vigilarse para no sobreajustar el benchmark.'),
 box('<b>Activo y aprendiendo:</b> el modelo vigente sigue atendiendo consultas mientras se evalúan candidatos. Solo una adopción cambia el despliegue; los resultados previos y las selecciones ya iniciadas se conservan.'),
])
page(full,11,'Métricas y estado consultado',[
 table(['Mercado','Fase','Modelo activo','Ejemplos'],modelrows(),[95,50,225,WIDTH-370]),Spacer(1,10),
 table(['OLS previo','Decisión','MAE candidato','MAE base'],linearrows(),[100,140,110,WIDTH-350]),
 p('Instantánea local del 25/10/2026. Los ejemplos indican disponibilidad de datos elegibles, no partidos nuevos evaluados prospectivamente ni garantía de precisión. La fila de modelo activo y el último intento de entrenamiento pueden corresponder a revisiones diferentes.','small'),
 sub('Cómo leer las métricas'),p('<b>Accuracy:</b> porcentaje de clase más probable acertada. <b>Log loss:</b> penaliza probabilidades incorrectas, especialmente cuando son muy confiadas. <b>Brier:</b> distancia cuadrática entre probabilidades y resultado (rango multiclase usado: 0 a 2). <b>MAE:</b> promedio de |real - estimado| para cantidades.'),
 p('El sistema selecciona por log loss, no por el porcentaje de apuestas acertadas. En conteos usa la pérdida de la distribución Poisson completa; también reporta MAE. La matriz de confusión, precisión, recall y F1 ayudan a revisar errores por clase. No deben mezclarse métricas de previo y en vivo como si fueran una sola prueba.'),
])
page(full,12,'Momios como referencia adicional',[
 p('The Odds API aporta cuotas previas cuando hay cobertura y coincidencia de equipos y hora. No hay integración confirmada de momios de Draftea. Los mercados consultados son resultado 1X2 y total de goles; no se presupone cobertura de córners y tarjetas.'),
 box('probabilidad implícita = 1 / cuota_decimal<br/>p_sin_margen(i) = (1 / cuota_i) / suma(1 / cuota_j)',True),
 p('La política stable-market-v1 construye una referencia robusta por mercado. Exige al menos tres grupos de fuentes válidas, filtra discrepancias y compara la misma línea para goles. Agrupar marcas relacionadas evita contarlas como confirmaciones totalmente separadas; no prueba independencia entre casas.'),
 table(['Situación','Aporte inicial experimental'],[['Una captura y concordancia transversal suficiente','10% de referencia de mercado.'],['Capturas comparables con estabilidad temporal','Hasta 20%.'],['Datos antiguos, insuficientes o mercado con movimiento excesivo','0%; se conserva la salida deportiva.']],[310,WIDTH-310]),
 sub('Calidad frente a certeza'),p('Se admiten cuotas con antigüedad limitada; el filtro usa dispersión máxima de ocho puntos porcentuales. La estabilidad temporal requiere capturas separadas al menos 30 minutos, comparables dentro de 48 horas, con movimiento máximo de cuatro puntos. El refresco diario no equivale a estabilidad minuto a minuto.'),
 p('Los pesos 10%/20% son reglas experimentales, no una mejora ya aprendida. Un combinador puede reemplazarlos después de evaluación temporal con suficientes ejemplos prospectivos, incluso con peso cero. No se trasladan cuotas previas al motor en vivo como si fueran cuotas actuales.'),
])
page(full,13,'Selecciones automáticas y evaluación',[
 p('Las apuestas automáticas son registros de simulación sin dinero. Se generan a partir de pronósticos elegibles de resultado, goles, córners y amarillas. Cada registro conserva probabilidad, selección, fase, política, revisión y fecha.'),
 Flow(['Pronóstico|elegible','Selección|registrada','Resultado|confirmado','Acierto|o fallo']),
 sub('Ejemplo'),p('Una selección de menos de 3.5 goles acierta con un total final de tres y falla con cuatro. La evaluación de córners necesita el contador final de córners; no basta con que el partido tenga marcador final. Si falta el dato, no se inventa una liquidación.'),
 sub('Estados'),table(['Estado','Significado'],[['Pendiente','Todavía falta resultado o estadística final utilizable.'],['Acertada / fallida','La selección se comparó con el dato final correspondiente.'],['Anulada / retirada','La selección no debe evaluarse normalmente por una condición de invalidez o falta de respaldo.']],[130,WIDTH-130]),
 sub('Revisiones y doble oportunidad'),p('Antes del inicio pueden revisarse selecciones automáticas futuras al cambiar el modelo o el aporte de mercado, conservando auditoría. Las selecciones empezadas no se reescriben para mejorar el historial. Una política puede proponer doble oportunidad si ciertas probabilidades son cercanas; es una regla de selección y no un modelo de aprendizaje adicional.'),
 box('<b>El modelo aprende de resultados confirmados.</b> Elegir una apuesta no la vuelve una etiqueta verdadera. Acertar una simulación tampoco demuestra rentabilidad: sin cuotas y costes evaluados no puede inferirse rendimiento económico.'),
])
page(full,14,'Interfaz y seguimiento de partidos',[
 table(['Ruta','Contenido'],[['/ y /en-vivo','Jornada, filtros y encuentro destacado.'],['/match/:id','Marcador, cancha vinculada o eventos, estadísticas y análisis.'],['/plantillas y /equipo/:id','Equipos, jugadores y detalles disponibles.'],['/posiciones','Clasificación por competición.'],['/cartelera','Calendario de encuentros compatibles.'],['/mis-pronosticos','Selecciones simuladas y resultados de la cuenta.'],['/admin y /admin/login','Acceso y módulos de administración.']],[170,WIDTH-170]),
 sub('Cancha real del mismo encuentro'),p('LiveCoverage solo muestra el iframe de SportScore si existe una vinculación verificada para el partido. Si no existe, muestra eventos y estadísticas ESPN, sin cancha ilustrativa ni partido ajeno. Las estadísticas van al costado en escritorio y se apilan en móvil.'),
 p('La vinculación general automática todavía no está implementada. El registro actual contiene dos pilotos fechados del 23/10/2026: Al Faisaly-Al Nassr e Ipswich-Nottingham. Se comprueban equipos, liga, hora, estado LIVE y una ventana de cuatro horas. No son una cobertura permanente para todos los partidos. La animación del proveedor no garantiza coordenadas físicas continuas del balón.'),
 sub('Fecha, reloj y accesibilidad'),p('Las horas se presentan en America/Hermosillo, UTC-7. Los segundos pueden interpolarse entre minutos publicados y se identifican como aproximados. Eso no crea eventos deportivos. El diseño incorpora modo claro/oscuro, preferencia local, navegación móvil y estados de datos faltantes.'),
])
page(full,15,'Seguridad, cuentas y API',[
 p('La autenticación disponible es inicio y cierre de sesión. Las contraseñas se verifican con bcrypt; no se guardan en texto plano en la tabla de usuarios. Las sesiones usan cookies, con HttpOnly y controles SameSite; Secure depende de la configuración de despliegue. Se verifican permisos y CSRF en operaciones protegidas.'),
 p('El acceso administrativo comprueba el rol y la cuenta persistida. El sistema registra intentos de acceso y aplica bloqueo temporal. CORS restringe orígenes configurados. Las entradas se validan mediante modelos y parámetros de FastAPI/Pydantic.'),
 sub('Gestión de secretos'),p('Las claves de proveedores y APP_SECRET deben mantenerse en .env, excluido de Git. No deben ponerse secretos en variables VITE_* porque terminan en el navegador. Los alias públicos de widgets son distintos de las claves REST privadas. Este documento no contiene credenciales.'),
 table(['Servicio representativo','Acceso / propósito'],[['GET /api/v1/health, /leagues, /feed','Lecturas públicas de salud, ligas y jornada.'],['GET /api/v1/matches/{id}, /teams/{id}','Detalle público de entidades.'],['GET /api/v1/leagues/{code}/standings','Tabla de posiciones.'],['GET /api/v1/learning','Estado del aprendizaje.'],['GET /api/v1/metrics, /models/audit','Métricas y auditoría administrativa.'],['POST /api/v1/feed/refresh, /odds/sync','Operaciones administrativas protegidas.'],['/api/v1/auth/login, /logout, /me, /csrf','Sesión, usuario actual y protección de solicitudes.']],[255,WIDTH-255]),
 box('<b>Requisito académico por completar:</b> no se encontró una ruta/pantalla de autorregistro de usuarios en la versión revisada. El login existente no debe presentarse como un registro con validación ya implementado.'),
])
page(full,16,'Instalación, ejecución y PWA',[
 sub('Arranque en Windows'),box('cd C:\\Users\\Jorge\\Desktop\\sport-analytics-platform<br/>.\\run.ps1',True),
 p('El script prepara dependencias si faltan y arranca backend y frontend. Por defecto utiliza la compilación para PWA. Con .\\run.ps1 -Dev se usa Vite de desarrollo. Si un puerto ya está ocupado, conserva el proceso: eso no garantiza que ese proceso tenga la última compilación.'),
 table(['Dirección local','Uso'],[['http://127.0.0.1:5173','Sitio y administración bajo /admin.'],['http://127.0.0.1:8000/api/docs','OpenAPI en entornos donde está habilitado.'],['backend/data/forma.db','Base SQLite local de respaldo cuando corresponde.']],[265,WIDTH-265]),
 sub('Actualizar y verificar'),box('cd frontend<br/>npm run build<br/>npm test<br/><br/>cd ..\\backend<br/>.\\.venv\\Scripts\\python.exe -m pytest',True),
 p('Para cambios Python, reiniciar el proceso de API de este proyecto. Para cambios del frontend compilado, aceptar la actualización de la PWA o recargar cuando se publique la nueva versión. Antes de migraciones, respaldar la base y los modelos. No ejecutar varios schedulers contra el mismo SQLite.'),
 sub('Qué aporta la PWA'),p('Manifiesto, iconos, instalación compatible y archivos estáticos precacheados. No guarda sesiones, cuotas o marcadores como una supuesta fuente offline. Un teléfono necesita un despliegue HTTPS accesible para instalación normal; localhost solo apunta al dispositivo que lo abre. La cancha externa requiere conexión.'),
])
page(full,17,'Verificación, límites y referencias',[
 sub('Comprobaciones registradas'),p('La implementación de OLS incluyó pruebas de recuperación de una relación lineal, serialización JSON, exclusión de columnas sin observaciones, límites de conteos negativos, adopción temporal y conservación del incumbente sin prueba nueva. En la verificación final del 25/10/2026 se ejecutaron las suites completas: 108 pruebas backend y 17 frontend aprobadas; compilación PWA correcta. Se registró una advertencia de deprecación de una dependencia de pruebas. No equivale a certificar todo el producto ni una precisión futura.'),
 sub('Límites principales'),p('Cobertura y disponibilidad externas variables; diferencias de retraso entre ESPN y SportScore; independencia y dispersión imperfectas en Poisson; poco historial en vivo; comparación interna de modelos, sin auditoría externa; posibles fugas por revisiones históricas de proveedores; necesidad de coordinación para escalar; autorregistro pendiente y vínculos de cancha limitados a pilotos.'),
 sub('Referencias de implementación'),p('market_pipeline.py: evidencia, división temporal, especialistas y selección.<br/>linear_models.py: OLS, transformación y persistencia.<br/>forecasts.py: capturas, revisiones y resultados.<br/>stable_market.py y odds_feed.py: cuotas y combinación.<br/>scheduler.py: periodicidad.<br/>LiveCoverage.jsx y verifiedTrackers.js: cancha y estadísticas.<br/>security.py y auth.py: autenticación.<br/>vite.config.js y run.ps1: PWA y arranque.','small'),
 sub('Bibliografía técnica oficial'),p('scikit-learn - LinearRegression:<br/><link href="https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html" color="#B4461C">scikit-learn.org / LinearRegression</link><br/>CatBoost - How training is performed:<br/><link href="https://catboost.ai/docs/en/concepts/algorithm-main-stages" color="#B4461C">catboost.ai / algorithm-main-stages</link><br/>SciPy - Distribución Poisson (referencia matemática):<br/><link href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html" color="#B4461C">docs.scipy.org / scipy.stats.poisson</link><br/>SportScore - Widgets y condiciones:<br/><link href="https://sportscore.com/embed/" color="#B4461C">sportscore.com/embed</link>','small'),
 p('Referencias consultadas el 25/10/2026. La documentación en línea puede corresponder a versiones distintas de las dependencias fijadas en el repositorio. Algunos documentos antiguos conservan nombres FORMA/VELAR y fórmulas anteriores; no describen por sí solos la versión actual.','small'),
])
extras=[]
page(extras,1,'Planteamiento del proyecto',[
 p('<b>Problema:</b> consultar datos deportivos aislados no permite evaluar si un pronóstico se emitió con información válida ni si un cambio de modelo realmente mejora. Se necesita reunir datos, conservar decisiones y contrastarlas con resultados posteriores.'),
 sub('Justificación académica'),p('Nexo conecta bases de datos, web services y aprendizaje supervisado en un caso verificable. Las estadísticas alimentan un proceso ETL; las variables permiten entrenar y comparar modelos; el dashboard presenta evidencia y limitaciones, no solamente una selección final.'),
 sub('Objetivo general'),box('Construir una aplicación web de análisis de fútbol que transforme datos reales en pronósticos trazables y evalúe especialistas con validación temporal.'),
 sub('Objetivos específicos'),p('1. Integrar fuentes externas e identificar equipos y encuentros.<br/>2. Conservar datos, fechas de consulta y estados de calidad.<br/>3. Construir variables históricas sin usar resultados futuros.<br/>4. Implementar Poisson, regresión lineal OLS y CatBoost.<br/>5. Evaluar y versionar modelos por mercado y fase.<br/>6. Presentar calendario, estadísticas, aprendizaje y resultados en un dashboard.'),
 sub('Usuarios y alcance'),p('El visitante consulta información deportiva. La cuenta autenticada accede a selecciones simuladas; la administración consulta métricas y sincronización. La aplicación no coloca apuestas reales, no transmite dinero y no garantiza resultados. El proyecto se entrega como código y documentación; no como servicio público hospedado con disponibilidad garantizada.'),
])
page(extras,2,'Requisitos y criterios de aceptación',[
 table(['Requisito','Implementación verificable','Criterio'],[['ETL','live_feed.py, count_history.py y roster_feed.py.','Extrae datos, transforma identidades/fechas y persiste sin duplicar eventos.'],['Regresión lineal','linear_models.py; LinearRegression OLS.','Entrena con ejemplos previos y solo se adopta tras comparación temporal.'],['Árboles de decisión','market_pipeline.py; CatBoost.','Ensamble de árboles para resultado y cantidades; no árbol individual dibujado.'],['Dashboard','AdminHome.jsx y LearningPanel.jsx.','Muestra modelos, datos, métricas y fuentes.'],['API externa','ESPN y The Odds API opcional.','Identifica fuente y trata respuestas faltantes.'],['Persistencia','SQLAlchemy y esquema relacional.','Conserva resultados, capturas y versiones.'],['Seguridad','auth.py y security.py.','Login, hash, sesión, roles, CSRF y control de intentos.'],['Entrega','Código, README y PDF en MDP.','Clonable, con comandos y limitaciones explícitas.']],[92,218,WIDTH-310]),
 sub('Requisitos no funcionales'),p('Responsividad; temas claro/oscuro; trazabilidad de versiones; tratamiento de datos faltantes; separación de credenciales; consultas compartidas para limitar carga; instalabilidad PWA compatible. La latencia depende también del proveedor externo.'),
 box('<b>Estado pendiente que no se oculta:</b> no hay autorregistro público; no existe descubrimiento automático general de canchas; un único árbol individual visualizado no forma parte del dashboard. Si la rúbrica exige esas funciones por separado, requieren trabajo adicional.'),
])
page(extras,3,'ETL: extracción, transformación y carga',[
 Flow(['E|Extraer','T|Transformar','L|Cargar','Verificar|y consultar']),
 sub('Extracción'),p('El scheduler invoca sync_feed, que consulta calendarios de las competiciones configuradas y resúmenes necesarios. Se reutilizan respuestas mediante caché y se registra el estado de cada fuente. Los directorios y plantillas tienen su trabajo periódico; las cuotas se solicitan por separado cuando hay clave y cobertura.'),
 sub('Transformación'),p('Se valida que el evento tenga identificador, competidores y fecha. Se resuelven equipos por su identidad; se convierten fechas a instantes con zona horaria; se normalizan estados como programado, en vivo y finalizado; se interpretan los contadores publicados. Un mismo proveedor/evento debe referirse al mismo encuentro.'),
 sub('Carga'),p('persist_event busca el registro por provider y provider_id. Si existe, actualiza información confirmada; si no, crea el encuentro. Se guardan consulta, estado y detalles. La ingesta de un refresco no debe producir un partido nuevo por cada minuto. Las capturas de pronóstico y cuotas mantienen su propia trazabilidad.'),
 sub('Ejemplo de recorrido'),box('Evento externo con fecha UTC y dos equipos -> identidad interna y estado normalizado -> Match y datos asociados -> variables anteriores al inicio -> pronóstico versionado -> comparación con resultado final.'),
 sub('Errores y recuperación'),p('Si el proveedor no responde o falta un campo, la interfaz conserva el último estado recibido o indica indisponibilidad. Un campo vacío no se interpreta como cero. El trabajo debe liberar bloqueos y cerrar sesiones aun si falla. Los errores se registran localmente; los logs y cachés privados no se publican en GitHub.'),
 p('La transformación de variables para entrenamiento es una etapa posterior a la ingesta: agrega antecedentes y no modifica los hechos deportivos originales.','small'),
])
page(extras,4,'Modelo de datos y relaciones',[
 Flow(['League|competición','Team|equipo','Match|encuentro','Snapshot|pronóstico']),
 table(['Relación principal','Cardinalidad y finalidad'],[['League - Team / Match','Una liga agrupa varios equipos y encuentros.'],['Team - Player','Un equipo puede registrar varios jugadores disponibles.'],['Match - equipos','Cada encuentro referencia un equipo local y uno visitante.'],['Match - ForecastSnapshot','Un encuentro conserva varias capturas por fase y momento.'],['ForecastRevision - ForecastSnapshot','Una revisión versiona múltiples capturas.'],['ForecastSnapshot - ForecastSelection','Una captura puede originar varias selecciones.'],['User - ForecastSelection','Cada selección pertenece a una cuenta.'],['Match - CountObservation / OddsObservation','Evidencias y cuotas se relacionan con el encuentro.'],['MarketLearner - ShadowForecast','Candidatos CatBoost registran pruebas en sombra.']],[230,WIDTH-230]),
 sub('Claves y restricciones'),p('Los IDs internos son claves de la aplicación; provider_id identifica eventos externos. ForecastSnapshot usa una huella única. Las selecciones tienen restricciones de unicidad por usuario, captura, mercado y línea. Los vínculos automáticos evitan duplicaciones por usuario, encuentro y mercado. El archivo models.py contiene los nombres y claves foráneas exactos.'),
 sub('Separación entre dato, estimación y decisión'),p('Match registra el hecho deportivo; MarketLearner conserva parámetros aprendidos; ForecastSnapshot contiene una estimación fechada; ForecastSelection contiene la decisión simulada. Separar estas entidades evita que una nueva predicción sobrescriba lo que se había decidido antes.'),
 p('En GitHub, docs/DIAGRAMAS.md incluye diagramas Mermaid navegables y el modelo conceptual. No se entrega una copia de la base con usuarios o sesiones.','small'),
])
page(extras,5,'Manual del dashboard',[
 table(['Tarea','Pasos y resultado esperado'],[['Consultar jornada','Abrir Inicio; seleccionar liga, fecha y estado; buscar un equipo. Los resultados respetan esos filtros.'],['Revisar un partido','Abrir Ver partido; consultar marcador, resumen, estadísticas y plantillas según cobertura.'],['Ver cancha','Si el mismo encuentro tiene vínculo verificado, se carga SportScore y estadísticas al costado. Si no, solo eventos y estadísticas.'],['Revisar pronósticos','Iniciar sesión y consultar previo y en vivo por separado; los mercados sin evidencia se indican como no disponibles.'],['Evaluar selecciones','Abrir Mis apuestas o Apuestas automáticas del panel; consultar pendiente, acertada, fallida o anulada.'],['Examinar aprendizaje','Administración > Modelos y aprendizaje: familia activa, candidatos, muestras y métricas.'],['Auditar datos','Abrir Datos de entrenamiento y Resultados y métricas; revisar cobertura y exclusiones.'],['Cambiar apariencia','Usar el botón de sol/luna; la preferencia se conserva localmente.']],[100,WIDTH-100]),
 sub('Interpretación responsable'),p('Un porcentaje es una estimación del modelo, no una estadística observada del partido. Un total esperado admite decimales. La simulación no afecta la estadística en vivo. Una selección pendiente no es un fallo ni un acierto. La hora de captura permite detectar información atrasada.'),
 sub('Presentación para evaluación'),p('Demostrar filtros y dashboard; mostrar un registro de pronóstico y su versión; explicar la elegibilidad de datos; abrir la sección de regresión lineal; presentar métricas con su muestra y fase. No hace falta esperar un partido en vivo para explicar la arquitectura o las pruebas automatizadas.'),
])
page(extras,6,'Entrega, reproducción y pruebas',[
 box('<b>Repositorio de entrega:</b><br/><link href="https://github.com/GeorgieRe2rn/MDP" color="#B4461C">https://github.com/GeorgieRe2rn/MDP</link>'),
 sub('Reproducción desde GitHub'),p('Clonar MDP, copiar .env.example a .env, configurar un APP_SECRET propio e iniciar con .\\run.ps1. Consultar README para Python, Node, comandos manuales y puertos. La cuenta administrativa inicial se genera localmente; sus credenciales nunca forman parte del repositorio.'),
 p('La entrega contiene código, pruebas, archivos de ejemplo, informe Markdown, PDF, diagramas y evidencia de evaluación. Excluye .env real, claves, contraseñas, sesiones, SQLite, entornos virtuales, node_modules, logs y temporales. Una instalación limpia no hereda los modelos aprendidos de la base local: debe recopilar y entrenar con evidencia propia.'),
 sub('Verificación ejecutada el 25/10/2026'),table(['Comprobación','Resultado'],[['Backend: python -m pytest -q','108 pruebas aprobadas.'],['Frontend: npm test','17 pruebas aprobadas.'],['Frontend: npm run build','Compilación PWA correcta.'],['Advertencias','Deprecación de una dependencia de pruebas; sin fallos.'],['Documentación','PDF renderizados y revisados visualmente; enlaces y contenido comprobados.']],[250,WIDTH-250]),
 sub('Qué cubren las pruebas'),p('Fechas y zonas horarias; filtros; eventos y relojes; identidad de encuentros; historial de conteos; métricas; momios; separación temporal; exclusión de información futura; serialización y adopción de OLS; preservación de modelos vigentes. Las pruebas no equivalen a disponibilidad permanente de APIs externas ni a precisión garantizada.'),
 sub('Criterio de entrega'),p('El lector debe poder localizar los cuatro requisitos centrales, instalar el proyecto, ejecutar las pruebas y distinguir funciones existentes de pendientes. El informe describe el estado revisado y conserva las limitaciones, no simula un producto terminado sin restricciones.'),
])

# Insert formal academic sections and a page-numbered table of contents.
cut=next(i for i,x in enumerate(full) if isinstance(x,PageBreak))
formal=extras[1:]
toc_page=[PageBreak(),p('GUÍA DE LECTURA','eyebrow'),p('Índice de contenidos','h1')]
combined=full[:cut]+toc_page+[PageBreak()]+formal+full[cut:]
chapter=0
for item in combined:
    if isinstance(item,Paragraph) and item.style.name=='Eye' and '/ DOCUMENTACIÓN DEL PROYECTO' in item.getPlainText():
        chapter+=1;item.text=f'{chapter:02d} / DOCUMENTACIÓN DEL PROYECTO';item.frags=p(item.text,'eyebrow').frags
titles=[];num=1
for item in combined:
    if isinstance(item,PageBreak):num+=1
    if isinstance(item,Paragraph) and item.style.name=='H1' and num>2:titles.append((item.getPlainText(),num))
toc=Table([[p(title,'cell'),p(str(n),'cell')] for title,n in titles],colWidths=[WIDTH-40,40])
toc.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,0),(-1,-1),.4,EDGE)]))
insert_at=cut+3
combined.insert(insert_at,toc)
full=combined

def export_markdown(path,story,title):
    lines=['# '+title,'','Corte: 25 de octubre de 2026. Repositorio: https://github.com/GeorgieRe2rn/MDP','']
    for item in story:
        if isinstance(item,Paragraph):
            text=item.getPlainText()
            if item.style.name=='H1':text='## '+text
            elif item.style.name=='H2':text='### '+text
            elif item.style.name=='Eye':continue
            lines.extend([text,''])
        elif isinstance(item,Table):
            for i,row in enumerate(item._cellvalues):
                values=[' '.join(v.getPlainText() if isinstance(v,Paragraph) else str(v) for v in (cell if isinstance(cell,(list,tuple)) else [cell])) for cell in row]
                lines.append('| '+' | '.join(v.replace('|','/') for v in values)+' |')
                if i==0:lines.append('| '+' | '.join('---' for _ in values)+' |')
            lines.append('')
        elif isinstance(item,Flow):lines.extend([' -> '.join(x.replace('|',' ') for x in item.labels),''])
    (ROOT/path).write_text('\n'.join(lines),encoding='utf-8')

emit('NEXO_Documentacion_Completa.pdf',full,'Documentación completa')
export_markdown('docs/ENTREGA_ACADEMICA.md',full,'Nexo - documentación completa de entrega')

brief=cover('Lo esencial<br/>para exponer','Qué hace Nexo y cómo utiliza Poisson, regresión lineal y CatBoost.','Guía breve para explicar el proyecto a la maestra. Incluye conceptos, funcionamiento real, evaluación y respuestas a preguntas frecuentes.')
page(brief,1,'El proyecto en un minuto',[
 box('Nexo convierte datos reales de fútbol en pronósticos evaluables. Recopila información, la limpia, construye variables, calcula probabilidades y compara sus decisiones con resultados confirmados.'),
 Flow(['Datos|reales','Historial|y variables','Modelos|por mercado','Evaluación|de resultados']),
 sub('Qué analiza'),p('Ganador o empate, goles, córners y amarillas. Separa el pronóstico previo del análisis en vivo. Las apuestas son simulaciones sin dinero; sirven para llevar un registro verificable de aciertos, fallos y datos pendientes.'),
 sub('Tecnologías y fuentes'),p('<b>React:</b> interfaz. <b>FastAPI/Python:</b> servicios y modelos. <b>SQLAlchemy con PostgreSQL o SQLite:</b> persistencia. <b>ESPN:</b> datos deportivos. <b>The Odds API:</b> referencia de cuotas. <b>SportScore:</b> cancha externa cuando existe una vinculación segura.'),
 sub('Relación con KDD'),p('Selección de datos, limpieza, transformación, minería y evaluación. Por ejemplo, resultados anteriores se transforman en promedios ofensivos/defensivos, puntos y descanso; después se relacionan con resultados finales para aprender y medir errores.'),
 box('<b>Frase clave:</b> los datos del partido son observaciones; las probabilidades son estimaciones. Si falta una estadística real, no se presenta un valor inventado como dato del equipo.'),
])
page(brief,2,'Los tres métodos principales',[
 table(['Método','Qué hace en Nexo','Idea para explicarlo'],[['Poisson','Convierte una tasa esperada en probabilidades de cantidades y marcadores.','¿Qué probabilidades tienen 0, 1, 2 o más eventos?'],['Regresión lineal OLS','Aprende una suma ponderada de variables para estimar goles, córners y amarillas.','Cada variable aporta un efecto lineal a la cantidad estimada.'],['CatBoost','Combina árboles para clasificación 1X2 y regresión de conteos.','Muchos árboles sucesivos intentan reducir el error del conjunto.']],[100,218,WIDTH-318]),
 sub('Poisson'),box('P(X = k) = exp(-lambda) * lambda^k / k!',True),
 p(f'Lambda es la cantidad esperada. Con lambda = 2.8, P(tres goles o más) es aproximadamente {poisson_example*100:.1f}%. Ejemplo didáctico, no un partido real.'),
 sub('Regresión lineal'),box('y_estimado = b0 + b1*x1 + b2*x2 + ...',True),
 p('OLS aprende coeficientes usando resultados conocidos. En Nexo se ajusta por mercado y fase; su tasa se combina con la base y se proyecta con Poisson. Se limitan los conteos negativos como regla explícita del modelo.'),
 sub('CatBoost'),p('Un árbol divide ejemplos mediante condiciones aprendidas, como promedios de goles o descanso. CatBoost combina muchos árboles para capturar relaciones no lineales. CatBoostRegressor no significa regresión lineal: ambas técnicas están implementadas por separado.'),
])
page(brief,3,'Cómo aprende y cómo se comprueba',[
 p('Es <b>aprendizaje supervisado por lotes</b>: cada ejemplo contiene variables anteriores y una etiqueta real confirmada. Las revisiones se programan cada seis horas, mientras el modelo activo sigue funcionando.'),
 Flow(['60%|Entrenamiento','20%|Validación','20%|Prueba','Mejora real|o conservar']),
 p('Se requieren al menos 200 ejemplos utilizables y tamaños mínimos por bloque. Se respetan fechas y separaciones de tres horas. Para en vivo, muchos minutos del mismo partido no cuentan como muchos partidos independientes.'),
 sub('Decisión de adopción'),p('El peso entre base y especialista se elige en validación. Después, el candidato debe mejorar la pérdida de prueba frente a la base y al modelo vigente por más de 0.002. Si no lo logra, el sistema conserva el modelo anterior.'),
 table(['Métrica','Interpretación'],[['Accuracy','Porcentaje de resultado 1X2 elegido correctamente.'],['Log loss','Calidad de probabilidades; castiga la confianza equivocada.'],['Brier','Distancia entre probabilidades y resultado real.'],['MAE','Error promedio en la cantidad estimada.']],[100,WIDTH-100]),
 box('<b>Cuidado al exponer:</b> la primera prueba de OLS es un benchmark histórico interno, no una garantía prospectiva ni una prueba externa. Tener un modelo entrenado no significa que esté activo o que sea mejor para todos los mercados.'),
])
page(brief,4,'Qué está activo y qué decir',[
 table(['Mercado','Previo activo','En vivo activo'],[[names[r['market']],r['active'],next(v['active'] for v in SNAP if v['market']==r['market'] and v['phase']=='LIVE')] for r in SNAP if r['phase']=='PRE'],[108,192,WIDTH-300]),
 p('Estado local consultado el 25/10/2026. OLS mejoró el benchmark de goles y córners previos; en amarillas se conserva CatBoost. Los candidatos en vivo esperan evidencia suficiente. Los modelos pueden cambiar tras evaluaciones posteriores.','small'),
 sub('Preguntas que puede hacer la maestra'),
 p('<b>¿Aprende solo?</b> Sí: recopila resultados y revisa candidatos por lotes. No cambia automáticamente solo porque pase el tiempo.'),
 p('<b>¿Por qué varios métodos?</b> Porque un clasificador de ganador no resuelve igual una cantidad de córners. Se compara cada mercado y fase con su base.'),
 p('<b>¿Usa momios?</b> Sí, cuando hay datos válidos. El aporte inicial de 10%/20% es experimental; no demuestra por sí solo mayor precisión.'),
 p('<b>¿La cancha entrena el modelo?</b> No. SportScore es visualización y aún requiere vínculos verificados; sin cancha se muestran estadísticas reales.'),
 p('<b>¿Garantiza acertar?</b> No. La aportación es analizar, medir y conservar trazabilidad. Un acierto aislado no valida el sistema.'),
 sub('Cierre listo para decir'),p('“Mi proyecto aplica KDD para transformar datos reales en pronósticos medibles. Compara Poisson, regresión lineal y CatBoost por mercado y fase; evalúa con partidos posteriores y solo adopta mejoras comprobadas internamente.”','quote'),
 p('Apoyo técnico: LinearRegression de scikit-learn, documentación de entrenamiento CatBoost y distribución Poisson de SciPy. Las referencias completas y los límites de implementación están en el documento técnico complementario.','small'),
])
emit('NEXO_Resumen_Exposicion.pdf',brief,'Resumen para exposición')
export_markdown('docs/RESUMEN_EXPOSICION.md',brief,'Nexo - resumen para exposición')

