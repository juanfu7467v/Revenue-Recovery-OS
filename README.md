# Revenue-Recovery-OS: Cashflow Recovery API (Producción)

## Infraestructura Financiera de Recuperación de Liquidez

**Revenue-Recovery-OS** es una plataforma diseñada para la recuperación automatizada de ingresos perdidos por pagos fallidos. Arquitectura **no custodia**, **escalable** y **segura**.

---

## 🚀 Nuevas Mejoras Implementadas

Hemos transformado el sistema en una solución de nivel empresarial con las siguientes funcionalidades:

### 🎨 1. Personalización Avanzada (Marca Blanca)
Permite a las empresas mantener su identidad visual en todas las comunicaciones de cobro para aumentar la confianza y evitar ser marcados como spam.
*   **Editor de Marca:** Configuración de logo, colores corporativos y tono del mensaje.
*   **Tono de Comunicación:** Selector de tono (**Profesional, Cercano, Urgente**) que adapta automáticamente el cuerpo de los correos.
*   **Endpoints:**
    *   `GET /api/v1/organization/branding`: Obtener configuración actual.
    *   `POST /api/v1/organization/branding`: Actualizar logo, colores y tono.

### 💰 2. Dashboard de "Dinero Recuperado"
Visualización clara del impacto económico directo del sistema.
*   **Mensaje Motivador:** "Este mes has recuperado $X,XXX USD que dabas por perdidos".
*   **Métricas Clave:**
    *   **Monto Recuperado:** Total histórico de dinero rescatado.
    *   **Tasa de Recuperación:** Porcentaje de éxito sobre pagos fallidos.
    *   **Campañas Activas:** Número de procesos de recuperación en curso.
*   **Endpoint:** `GET /api/v1/dashboard/metrics` (Ahora con datos extendidos).

### ⚡ 3. Prevención Proactiva (Pre-Dunning)
Evita los fallos de pago antes de que ocurran, notificando a los clientes sobre tarjetas próximas a vencer.
*   **Detección Automática:** Monitoreo de eventos de suscripción para identificar métodos de pago que caducan pronto.
*   **Notificaciones:** Envío automático de mensajes: *"Tu tarjeta vence pronto. Actualízala aquí para evitar interrupciones en el servicio"*.
*   **Webhook:** Soporte para `customer.subscription.updated` con lógica de prevención.

---

## Implementación Técnica de Producción

### 1. Seguridad (Blindaje)
*   **Auth Layer (JWT):** Todos los endpoints críticos (`/dashboard`, `/organization`) están protegidos.
*   **Vault (AES-256):** Las API Keys de Stripe/Adyen se almacenan encriptadas en Firestore usando la librería `cryptography`.

### 2. Base de Datos Firestore (Estructura)
*   `organizations`: Perfiles de clientes, planes, estado y **configuración de branding**.
*   `vault`: Almacén seguro de credenciales de procesadores de pago.
*   `recovery_events`: Auditoría real de cada webhook recibido.
*   `recovery_logs`: Seguimiento detallado de cada factura en proceso de recuperación.

### 3. Webhook Listener "Live"
*   Endpoint: `/api/v1/webhooks/stripe`
*   Procesamiento en segundo plano (`BackgroundTasks`) para ejecutar Smart Retries, Dunning personalizado y **Pre-Dunning**.

---

## Guía de Despliegue en Fly.io

1.  **Configurar Secretos:** `ENCRYPTION_KEY`, `SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` y credenciales de Firebase.
2.  **Desplegar:** `fly deploy`.

## Flujo de Trabajo para Usuarios Reales

1.  **Registro:** El usuario se registra vía `/api/v1/auth/register`.
2.  **Configuración de Marca:** Define su logo y tono en `/api/v1/organization/branding`.
3.  **Conexión:** Guarda su API Key de Stripe vía `POST /api/v1/organization/vault/api-key`.
4.  **Activación:** Configura el Webhook en Stripe.
5.  **Monitoreo:** Observa el dinero recuperado en tiempo real en el Dashboard.

---
**Autor:** Manus AI
**Estado:** Mejorado y Listo para Producción
