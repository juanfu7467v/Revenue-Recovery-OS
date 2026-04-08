# Revenue-Recovery-OS: Cashflow Recovery API

## Descripción General

**Revenue-Recovery-OS** es una plataforma tipo "Cashflow Recovery API" diseñada para ayudar a las empresas a recuperar ingresos perdidos debido a pagos fallidos o facturas vencidas. El sistema se integra con procesadores de pago como Stripe y Adyen (la integración con Adyen se puede añadir fácilmente siguiendo el patrón de Stripe) para automatizar y optimizar el proceso de recuperación de fondos. La arquitectura es **no custodia**, lo que significa que el dinero nunca pasa por nuestra plataforma, sino que va directamente del procesador de pagos a la cuenta del cliente.

## Características Principales (MVP)

### 1. Smart Retries

Implementa reintentos automáticos e inteligentes de cobros fallidos. Utiliza datos y eventos (webhooks) para determinar la estrategia óptima de reintento, mejorando las tasas de recuperación.

### 2. Dunning Multicanal

Envío automático de recordatorios de pago a través de múltiples canales, incluyendo Email, WhatsApp y SMS. La lógica de dunning puede ser personalizada para adaptarse a las necesidades de cada negocio.

### 3. Scoring de Recuperación

Un sistema simple que prioriza las facturas con mayor probabilidad de ser pagadas. Esto permite a las empresas enfocar sus esfuerzos de recuperación de manera más eficiente.

### 4. Panel de Control (Dashboard Simple)

Un panel de control que proporciona al usuario tres métricas clave para monitorear el rendimiento de la recuperación:

*   **Dinero recuperado:** El monto total de fondos recuperados por la plataforma.
*   **Reducción en días de cobro:** La mejora en el tiempo promedio para cobrar facturas.
*   **Cuentas en riesgo:** El número de cuentas con pagos pendientes que requieren atención.

## Arquitectura y Tecnología

El proyecto está construido con las siguientes tecnologías:

*   **Backend:** FastAPI (Python)
*   **Base de Datos:** Firebase Firestore
*   **Encriptación:** `cryptography` para tokens y API Keys sensibles.
*   **Despliegue:** Fly.io
*   **Contenedorización:** Docker

### Estructura del Proyecto

```
Revenue-Recovery-OS/
├── .github/
│   └── workflows/         # Flujos de trabajo de GitHub Actions (CI/CD)
├── .fly/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/   # Endpoints de la API (webhooks, dashboard)
│   │       ├── __init__.py
│   │       └── schemas.py   # Modelos de datos Pydantic
│   ├── database/
│   │   ├── firestore.py   # Configuración y cliente de Firebase Firestore
│   │   └── __init__.py
│   ├── services/
│   │   ├── dunning.py     # Lógica de Dunning Multicanal
│   │   ├── payment_processors/ # Integraciones con procesadores de pago (e.g., Stripe)
│   │   ├── scoring.py     # Lógica de Scoring de Recuperación
│   │   ├── smart_retries.py # Lógica de Smart Retries
│   │   └── __init__.py
│   ├── utils/
│   │   ├── encryption.py  # Utilidades de encriptación
│   │   └── __init__.py
│   ├── tests/             # Pruebas unitarias e de integración
│   ├── config.py          # Configuración de la aplicación
│   └── main.py            # Archivo principal de la aplicación FastAPI
├── .gitignore             # Archivos y directorios a ignorar por Git
├── Dockerfile             # Definición del contenedor Docker
├── firestore.rules        # Reglas de seguridad de Firebase Firestore
├── fly.toml               # Configuración de despliegue en Fly.io
└── requirements.txt       # Dependencias de Python
```

## Configuración y Despliegue

### Requisitos Previos

*   Python 3.9+
*   Docker
*   Cuenta de Firebase y proyecto configurado.
*   Cuenta de Fly.io y `flyctl` instalado.
*   `gh` CLI para interactuar con GitHub (ya configurado en el entorno de desarrollo).

### 1. Clonar el Repositorio

```bash
gh repo clone juanfu7467v/Revenue-Recovery-OS
cd Revenue-Recovery-OS
```

### 2. Configuración de Firebase

1.  Crea un proyecto en [Firebase Console](https://console.firebase.google.com/).
2.  Habilita Firestore Database.
3.  Genera una clave de cuenta de servicio (Service Account Key) en `Project settings > Service accounts`. Descarga el archivo JSON.
4.  Guarda el archivo JSON descargado como `firebase-adminsdk.json` en la raíz de tu proyecto o especifica la ruta en la variable de entorno `FIREBASE_CREDENTIALS_PATH`.
5.  Despliega las reglas de seguridad de Firestore (`firestore.rules`) usando Firebase CLI:
    ```bash
    firebase deploy --only firestore:rules
    ```

### 3. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```dotenv
DATABASE_URL=""
FIREBASE_CREDENTIALS_PATH="./firebase-adminsdk.json"
ENCRYPTION_KEY="tu_clave_secreta_de_32_bytes_para_encriptacion"
# Ejemplo de clave de encriptación (generar una nueva para producción):
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecución Local

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

La API estará disponible en `http://localhost:8000`.
La documentación interactiva de la API (Swagger UI) estará en `http://localhost:8000/docs`.

### 6. Despliegue en Fly.io

1.  Asegúrate de tener `flyctl` configurado y autenticado.
2.  Desde la raíz del proyecto, ejecuta:
    ```bash
    fly launch
    ```
    Sigue las instrucciones. `fly.toml` ya está configurado.
3.  Configura las variables de entorno en Fly.io:
    ```bash
    fly secrets set FIREBASE_CREDENTIALS_PATH="/path/to/your/firebase-adminsdk.json" ENCRYPTION_KEY="tu_clave_secreta"
    ```
    **Nota:** Para `FIREBASE_CREDENTIALS_PATH`, deberás subir tu archivo `firebase-adminsdk.json` de forma segura a Fly.io o configurar tus credenciales de Firebase de otra manera (e.g., como secretos de Fly.io si es posible, o montando un volumen). Para el MVP, se asume que el archivo estará disponible en la ruta especificada o que las credenciales se inyectarán como variables de entorno.
4.  Despliega la aplicación:
    ```bash
    fly deploy
    ```

## Uso de la API

### Webhooks (Stripe)

*   **Endpoint:** `/api/v1/webhooks/stripe`
*   **Método:** `POST`
*   **Descripción:** Recibe eventos de webhook de Stripe, como `invoice.payment_failed`, para iniciar el proceso de recuperación.

### Dashboard

*   **Endpoint:** `/api/v1/dashboard/metrics`
*   **Método:** `GET`
*   **Descripción:** Obtiene las métricas clave del dashboard para un usuario específico.
*   **Parámetros de consulta:** `user_id` (string)

## Próximos Pasos y Mejoras

*   **Integración de Autenticación:** Implementar autenticación de usuarios (e.g., JWT) para proteger los endpoints de la API.
*   **Manejo de Errores:** Mejorar el manejo de errores y logging.
*   **Integración con Procesadores de Pago:** Completar la integración con Stripe (reintentos reales) y añadir Adyen.
*   **Configuración de Dunning:** Permitir a los usuarios configurar sus propias reglas de dunning (canales, tiempos, mensajes).
*   **Interfaz de Usuario:** Desarrollar una interfaz de usuario (frontend) para el dashboard y la configuración.
*   **Pruebas:** Añadir pruebas unitarias y de integración exhaustivas.
*   **Monitoreo y Alertas:** Implementar monitoreo de la aplicación y alertas para eventos críticos.

---

**Autor:** Equipo infraestructura masitaprex 
**Fecha:** 08 de abril de 2026
