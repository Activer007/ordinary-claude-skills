

<p align="center">
  <a href="https://github.com/Microck/ordinary-claude-skills">
    <img src="https://i.ibb.co/Q3kYxbBt/claudeskills.png" alt="i drew this with my left hand. as you can deduce, im indeed right-handed" width="600">
  </a>
</p>

<p align="center">un repositorio local masivo de habilidades de claude oficiales y creadas por la comunidad, organizadas por categoría.</p>

<p align="center">
  <a href="https://microck.github.io/ordinary-claude-skills/#/"><img alt="docs" src="https://img.shields.io/badge/view-documentation-orange" /></a>
  <a href="https://github.com/Microck/ordinary-claude-skills/blob/main/LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-greene" /></a>
  <a href="https://github.com/Microck/ordinary-claude-skills"><img alt="maintenance" src="https://img.shields.io/badge/maintenance-passive-yellow" /></a>
  <a href="https://github.com/Microck/ordinary-claude-skills"><img alt="claude" src="https://img.shields.io/badge/AI-claude-purple" /></a>
</p>

---

## inicio rápido

hay dos formas de consumir esta biblioteca.

### 1. la forma civilizada (buscar y navegar)
ve al **[sitio estático](https://microck.github.io/ordinary-claude-skills/#/)**.
he indexado todo con búsqueda y categorías. es mucho más fácil que revolver por carpetas.

### 2. la forma de desarrollador (archivos crudos)
clona el repositorio para mapear estas habilidades en tus propios servidores mcp o agentes.

1.  **clona el repositorio**
    ```bash
    git clone https://github.com/Microck/ordinary-claude-skills.git
    cd ordinary-claude-skills
    ```

2.  **elige tu arma**
    *   **para claude.ai:** ve a tu perfil, haz clic en `custom skills`, y sube la carpeta específica de la habilidad que quieras.
    *   **para api/devs:** apunta tu cliente mcp o la configuración del prompt del sistema al directorio de la habilidad correspondiente.

3.  **verifica**
    pregúntale a claude `¿puedes usar la habilidad [nombre de la habilidad] ahora?`. si dice que sí, estás listo.

## índice de contenidos

*   [visión general](#overview)
*   [características](#features)
*   [catálogo de habilidades](#skill-catalog)
*   [configuración](#configuration)
*   [ejemplos prácticos](#how-to-examples)
*   [solución de problemas](#troubleshooting)
*   [dependencias](#dependencies)
*   [licencia y créditos](#license--credits)

## visión general

las habilidades son básicamente paquetes de prompts y scripts sofisticados que enseñan a claude a hacer cosas específicas sin que tengas que explicar el contexto cada vez. se cargan de forma perezosa (solo cuando se necesitan), lo que ahorra espacio en la ventana de contexto y evita que claude se confunda con instrucciones que aún no necesita.

este repositorio agrupa cientos de habilidades de anthropic, composiohq, k-dense-ai y genios aleatorios de internet.

## características

*   **selección sin curaduría:** metí de todo aquí. si no funciona, probablemente no me haya dado cuenta. avísame y quizás sí o quizás no lo arregle.
*   **categorizado:** todo está ordenado para que no tengas que hacer doomscroll buscando las herramientas de python.
*   **estandarizado:** intenté mantener las estructuras de carpetas algo consistentes.
*   **primero local:** diseñado para clonarse localmente, así no dependes de que una url de terceros se mantenga activa para siempre.

## catálogo de habilidades

suelo listar las más de 600 habilidades aquí, pero hacía que el readme se extendiera por la eternidad.

**[ver el inventario completo en el sitio de documentación →](https://microck.github.io/ordinary-claude-skills/#/)**

las categorías incluyen:
*   **ciencia y academia** (plegamiento de proteínas, astronomía, automatización de laboratorios)
*   **ingeniería de software** (diseño de apis, depuración, pruebas)
*   **infraestructura** (kubernetes, docker, terraform)
*   **datos y ia** (bases de datos vectoriales, evaluación de llms, rag)
*   **negocios** (marketing, finanzas, legal)
*   **creativo** (escritura, arte, filosofía)
*   **web3** (solidity, contratos inteligentes, defi)

<img width="1920" height="914" alt="page" src="https://github.com/user-attachments/assets/1fa2d35e-5c58-46a3-ac21-e6548853559b" />

## análisis de calidad

este repositorio ahora incluye un análisis exhaustivo de la calidad de las 415 habilidades.

**último análisis (2026-01-13):**
*   **puntuación promedio:** 61.6/100
*   **habilidades de alta calidad (nivel A):** 43 (10.4%)
*   **necesitan mejora (nivel D):** 151 (36.4%)

**ver informes:**
*   [resumen del análisis](reports/skills_analysis_summary.md) - visión general legible con estadísticas y clasificaciones
*   [top 100 de habilidades](reports/top_100_skills.md) - mejores recomendaciones de calidad
*   [candidatos a mejora](reports/improvement_candidates.md) - 151 habilidades que necesitan trabajo con sugerencias específicas

**ejecuta tu propio análisis:**
```bash
cd tools
source .venv/bin/activate
python scripts/analyze_all_skills.py
```

consulta [tools/scripts/README.md](tools/scripts/README.md) para la documentación completa del sistema de análisis.

**dimensiones de puntuación:**
*   **calidad del contenido (50 pts):** claridad, profundidad técnica, completitud de la documentación
*   **implementación técnica (30 pts):** calidad del código, patrones de diseño, manejo de errores
*   **mantenimiento (10 pts):** frecuencia de actualizaciones, actividad de la comunidad
*   **experiencia de usuario (10 pts):** facilidad de uso, legibilidad

**top 10 de habilidades de mayor calidad:**
1. python-packaging (88/100)
2. python-testing-patterns (87/100)
3. code-review-excellence (86/100)
4. biopython (85/100)
5. fda-database (84/100)
6. gpt5-consultant (84/100)
7. nodejs-backend-patterns (84/100)
8. spec-kit-skill (84/100)
9. api-design-principles (83/100)
10. auth-implementation-patterns (83/100)

## configuración

que esto funcione depende de tu entorno. esta es la forma recomendada de configurar las cosas si usas mcp o un cliente local.

### estructura de archivos

```text
ordinary-claude-skills/
├── docs/                  # los archivos del sitio web estático
├── skills_all/    		   # todo
├── skills_categorized/    # todo en su lugar correcto
│   ├── backend/
│   │   └── api-design-principles/
│   └── web3-tools/
│       └── solidity-security/
└── README.md
```

### ejemplo de config.json

si usas una herramienta que requiere un archivo de configuración para apuntar a las habilidades, generalmente se verá algo así.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/ordinary-claude-skills/skills_all"
      ]
    }
  }
}
```

o mapea solo la categoría o la habilidad específica que necesites.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/ordinary-claude-skills/skills_categorized/[category]"
      ]
    }
  }
}
```

## ejemplos prácticos

así es como realmente hablas con claude una vez que las habilidades están cargadas.

### escenario 1: depurando una aplicación de react

carga las habilidades `debugging-strategies` y `frontend-design`.

**tú:**
> tengo un componente de react que no está renderizando los elementos de la lista correctamente. por favor usa la habilidad de depuración sistemática para analizar el código que pegaré a continuación, y luego usa la habilidad de diseño frontend para proponer una solución.

**claude:**
> entendido. aplicaré el protocolo de depuración sistemática. por favor pega el código.

### escenario 2: analizando un competidor

carga la habilidad `competitive-ads-extractor`.

**tú:**
> aquí hay una url de una landing page. ejecuta el extractor de anuncios y dime cuál es su proposición de valor principal.

**claude:**
> ejecutando extracción...

### escenario 3: extracción de pdf
carga la habilidad `pdf`.

**tú:**
> un cliente acaba de enviarme una imagen escaneada de una hoja de cálculo pegada en un documento de word y luego exportada como pdf. estoy perdiendo las ganas de vivir. por favor usa la habilidad pdf para extraer el texto para que no tenga que caminar por la tabla.

**claude:**
> extrayendo texto ahora. por favor bebe un poco de agua mientras manejo este crimen contra las estructuras de datos.

### escenario 4: ruleta de despliegue
carga la habilidad `webapp-testing`.

**tú:**
> estoy a punto de hacer push a prod un viernes por la tarde. ejecuta la habilidad de testing de webapp en `localhost:3000` y dime si me van a despedido.

**claude:**
> iniciando pruebas de playwright. te sugiero mantener tu currículum actualizado por si acaso el modal de login se vuelve a romper.


## solución de problemas

a veces las computadoras son complicadas.

*   **claude se niega a usar la habilidad:**
    asegúrate de haberle dicho explícitamente a claude que la habilidad existe en el prompt del sistema o que el archivo se adjuntó correctamente al contexto del proyecto. usualmente solo no sabe que está ahí.

*   **error "archivo demasiado grande":**
    algunas de estas habilidades tienen carpetas de dependencias masivas. ignora `node_modules` dentro de las carpetas de habilidades. solo necesitas los scripts de origen y las instrucciones.

*   **habilidades que se contradicen:**
    no cargues `creative-writing` y `technical-documentation` al mismo tiempo. claude se confundirá sobre si debe actuar como shakespeare o como un robot.

## dependencias

técnicamente ninguna para el repositorio en sí, pero las habilidades individuales tienen requisitos.

*   **obligatorio:** una conexión a internet activa y una cuenta de claude (o clave api).
*   **opcional:**
    *   `python 3.x` (para habilidades de análisis de datos)
    *   `node.js` (para habilidades de constructor mcp y testing)
    *   `playwright` (si quieres hacer automatización de navegador)

## licencia y créditos

no escribí la mayoría de estas. solo las reuní.

*   **habilidades de anthropic:** licencia mit (en su mayoría)
*   **habilidades de la comunidad:** revisa el archivo `LICENSE` en cada carpeta específica.

los créditos van a [anthropic](https://github.com/anthropics), [composiohq](https://github.com/ComposioHQ), [k-dense-ai](https://github.com/K-Dense-AI) y a las demás leyendas listadas en las tablas de origen. si eres dueño de alguna de estas y quieres que la retire, solo abre un issue y la eliminaré.
