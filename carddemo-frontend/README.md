# CardDemo Frontend

Frontend Vue.js moderno para el sistema bancario CardDemo. Una aplicación web responsive construida con Vue.js 3, TypeScript y Tailwind CSS que proporciona una interfaz completa para la gestión de cuentas bancarias, tarjetas de crédito y transacciones.

## 🚀 Características

- ✅ **Vue.js 3** con Composition API y TypeScript
- ✅ **Diseño Responsive** mobile-first con Tailwind CSS
- ✅ **Autenticación JWT** con gestión de sesiones
- ✅ **Gestión de Estado** con Pinia
- ✅ **Internacionalización** (Español/Inglés)
- ✅ **Tema Claro/Oscuro** con persistencia
- ✅ **Gráficos Interactivos** con Chart.js
- ✅ **Testing Comprehensivo** con Vitest y Property-Based Testing
- ✅ **Optimización de Performance** con lazy loading y code splitting

## 🛠️ Stack Tecnológico

- **Framework**: Vue.js 3 con Composition API
- **Lenguaje**: TypeScript
- **Build Tool**: Vite
- **Estilos**: Tailwind CSS
- **Routing**: Vue Router 4
- **Estado**: Pinia
- **HTTP**: Axios
- **Gráficos**: Chart.js + vue-chartjs
- **I18n**: Vue I18n
- **Testing**: Vitest + Vue Test Utils + fast-check

## 📋 Prerrequisitos

- Node.js >= 20.19.0 || >= 22.12.0
- npm >= 9.0.0
- API CardDemo ejecutándose en http://localhost:8000

## 🚀 Instalación y Configuración

### 1. Clonar e instalar dependencias

\`\`\`bash
cd carddemo-frontend
npm install
\`\`\`

### 2. Configurar variables de entorno

\`\`\`bash
cp .env.example .env
\`\`\`

Editar `.env` según tus necesidades:

\`\`\`env
VITE_APP_TITLE=CardDemo
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_LOCALE=es
\`\`\`

### 3. Ejecutar en desarrollo

\`\`\`bash
npm run dev
\`\`\`

La aplicación estará disponible en http://localhost:3000

## 📝 Scripts Disponibles

- \`npm run dev\` - Ejecutar servidor de desarrollo
- \`npm run build\` - Construir para producción
- \`npm run preview\` - Previsualizar build de producción
- \`npm run test:unit\` - Ejecutar tests unitarios
- \`npm run test:coverage\` - Ejecutar tests con cobertura
- \`npm run type-check\` - Verificar tipos TypeScript
- \`npm run format\` - Formatear código con Prettier
- \`npm run lint\` - Verificar tipos y linting

## 🏗️ Estructura del Proyecto

\`\`\`
src/
├── components/          # Componentes reutilizables
│   ├── ui/             # Componentes base (botones, inputs, etc.)
│   ├── charts/         # Componentes de gráficos
│   └── layout/         # Componentes de layout
├── views/              # Páginas/vistas principales
├── stores/             # Pinia stores
├── services/           # Servicios y API client
├── composables/        # Composables reutilizables
├── types/              # Definiciones de tipos TypeScript
├── locales/            # Archivos de traducción
├── assets/             # Assets estáticos
│   └── styles/         # Estilos CSS
├── config/             # Configuración de la aplicación
└── router/             # Configuración de rutas
\`\`\`

## 🎨 Temas y Estilos

La aplicación soporta tema claro y oscuro con cambio dinámico. Los estilos están construidos con Tailwind CSS y incluyen:

- Paleta de colores personalizada
- Componentes base reutilizables
- Animaciones y transiciones suaves
- Diseño responsive mobile-first
- Soporte para modo oscuro

## 🌍 Internacionalización

Soporta múltiples idiomas:

- **Español (es)** - Idioma por defecto
- **Inglés (en)** - Idioma alternativo

Los archivos de traducción se encuentran en \`src/locales/\`.

## 🔐 Autenticación

La aplicación utiliza autenticación JWT con:

- Login/logout seguro
- Persistencia de sesión
- Renovación automática de tokens
- Protección de rutas
- Manejo de sesiones expiradas

## 📊 Funcionalidades Principales

### Dashboard
- Resumen de cuenta
- Transacciones recientes
- Información de tarjetas
- Gráficos de gastos

### Gestión de Tarjetas
- Lista de tarjetas de crédito
- Detalles de cada tarjeta
- Información de límites y saldos
- Enmascaramiento de información sensible

### Historial de Transacciones
- Lista paginada de transacciones
- Filtros avanzados (fecha, monto, tipo)
- Detalles de transacciones
- Búsqueda y ordenamiento

### Gestión de Perfil
- Visualización de información personal
- Edición de datos de contacto
- Validación de formularios
- Confirmación de cambios

## 🧪 Testing

El proyecto incluye testing comprehensivo:

### Unit Tests
- Componentes individuales
- Funciones utilitarias
- Casos específicos y edge cases

### Property-Based Tests
- Validación de propiedades universales
- Testing con inputs generados aleatoriamente
- Cobertura exhaustiva de casos

\`\`\`bash
# Ejecutar todos los tests
npm run test:unit

# Ejecutar tests con cobertura
npm run test:coverage

# Ejecutar tests en modo watch
npm run test:unit -- --watch
\`\`\`

## 🚀 Construcción para Producción

\`\`\`bash
# Construir para producción
npm run build

# Previsualizar build
npm run preview
\`\`\`

El build optimizado incluye:
- Code splitting automático
- Tree shaking
- Minificación
- Compresión de assets
- Source maps

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| \`VITE_APP_TITLE\` | Título de la aplicación | CardDemo |
| \`VITE_API_BASE_URL\` | URL base de la API | http://localhost:8000 |
| \`VITE_DEFAULT_LOCALE\` | Idioma por defecto | es |
| \`VITE_DEBUG_MODE\` | Modo debug | true |

### Personalización de Tailwind

Editar \`tailwind.config.js\` para personalizar:
- Colores del tema
- Fuentes
- Espaciado
- Breakpoints
- Animaciones

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama de feature (\`git checkout -b feature/nueva-funcionalidad\`)
3. Commit de cambios (\`git commit -am 'Agregar nueva funcionalidad'\`)
4. Push a la rama (\`git push origin feature/nueva-funcionalidad\`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es parte del sistema CardDemo para demostración de migración de mainframe a tecnologías modernas.

## 🆘 Soporte

Para soporte y preguntas:
- Revisar la documentación de la API en http://localhost:8000/docs
- Verificar que la API esté ejecutándose
- Revisar los logs del navegador para errores de JavaScript
- Verificar la configuración de variables de entorno

---

**Desarrollado con ❤️ usando Vue.js 3 + TypeScript + Tailwind CSS**