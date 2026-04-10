# Revenue-Recovery-OS: Cashflow Recovery API (Producción)

## Infraestructura Financiera de Recuperación de Liquidez

**Revenue-Recovery-OS** es una plataforma diseñada para la recuperación automatizada de ingresos perdidos por pagos fallidos. Arquitectura **no custodia**, **escalable** y **segura**.

## Implementación Técnica de Producción

### 1. Seguridad (Blindaje)
*   **Auth Layer (JWT):** Todos los endpoints críticos (`/dashboard`, `/organization`) están protegidos.
*   **Vault (AES-256):** Las API Keys de Stripe/Adyen se almacenan encriptadas en Firestore usando la librería `cryptography`. Nunca en texto plano.

### 2. Base de Datos Firestore (Estructura)
*   `organizations`: Perfiles de clientes, planes y estado.
*   `vault`: Almacén seguro de credenciales de procesadores de pago.
*   `recovery_events`: Auditoría real de cada webhook recibido.
*   `recovery_logs`: Seguimiento detallado de cada factura en proceso de recuperación.

### 3. Webhook Listener "Live"
*   Endpoint: `/api/v1/webhooks/stripe`
*   Respuesta instantánea (200 OK).
*   Procesamiento en segundo plano (`BackgroundTasks`) para ejecutar Smart Retries y Dunning sin bloquear la respuesta al procesador de pagos.

---

## Guía de Despliegue en Fly.io (Inmediato)

Para que el sistema sea funcional para usuarios reales este fin de semana, sigue estos pasos:

### 1. Configurar Secretos en Fly.io
Ejecuta los siguientes comandos en tu terminal con `flyctl`:

```bash
# 1. Clave de encriptación para el Vault (Debe ser una clave Fernet válida de 32 bytes)
fly secrets set ENCRYPTION_KEY="tu_clave_fernet_generada"

# 2. Clave secreta para firmar los JWT
fly secrets set SECRET_KEY="una_cadena_larga_y_aleatoria"

# 3. Secreto de Webhook de Stripe (Obtenido del dashboard de Stripe)
fly secrets set STRIPE_WEBHOOK_SECRET="whsec_..."

# 4. Credenciales de Firebase (Usando variables individuales configuradas en Fly.io)
# Asegúrate de que las siguientes variables estén presentes en tus secretos de Fly.io:
# FIREBASE_TYPE, FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY_ID, FIREBASE_PRIVATE_KEY, 
# FIREBASE_CLIENT_EMAIL, FIREBASE_CLIENT_ID, FIREBASE_AUTH_URI, FIREBASE_TOKEN_URI, 
# FIREBASE_AUTH_PROVIDER_X509_CERT_URL, FIREBASE_CLIENT_X509_CERT_URL, FIREBASE_UNIVERSE_DOMAIN
```

### 2. Desplegar
```bash
fly deploy
```

---

## Flujo de Trabajo para Usuarios Reales

1.  **Registro:** El usuario se registra vía `/api/v1/auth/register`.
2.  **Conexión:** El usuario guarda su API Key de Stripe vía `POST /api/v1/organization/vault/api-key`.
3.  **Activación:** El usuario configura el Webhook en Stripe apuntando a `https://tu-app.fly.dev/api/v1/webhooks/stripe`.
4.  **Recuperación:** Ante un fallo de pago, el sistema activa automáticamente la lógica y el dashboard muestra el impacto.

## Bloqueos Técnicos
**Ninguno.** El sistema está listo para la operación real. El código es limpio, modular y está preparado para escalar desde el lunes con los primeros usuarios.

---
**Autor:** Manus AI
**Estado:** Listo para Producción
