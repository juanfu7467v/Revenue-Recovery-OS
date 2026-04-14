# Documentación Técnica del API para el Panel de Control de Revenue-Recovery-OS

Esta documentación detalla los endpoints del API necesarios para el desarrollo de la interfaz de usuario del Panel de Control de Revenue-Recovery-OS. Se enfoca en el nuevo sistema de validación por token, la especificación de endpoints por pantalla, el manejo seguro de claves API y la gestión de webhooks, incluyendo las integraciones con diversos procesadores de pago.

## 1. Sistema de Validación por Token

El sistema ha sido simplificado para integrarse con interfaces externas. Se ha eliminado la lógica de registro e inicio de sesión interna. Ahora, cada petición debe ser validada mediante un token de acceso.

### 1.1. Uso del Token de Acceso

Para acceder a los recursos protegidos del API, el cliente debe incluir el token en el encabezado de la solicitud.

*   **Header:** `X-Token`
*   **Valor:** El token asignado a la empresa en la colección `empresas` de Firestore.

### 1.2. Validación del Token

Cada solicitud es validada contra la base de datos Firestore:
1. Se busca en la colección `empresas`.
2. Se compara el valor del campo `token`.
3. Solo se permite el acceso si existe una coincidencia exacta.

### 1.3. Endpoint de Verificación

**Endpoint:** `GET /api/v1/auth/validate-token`

Permite verificar si un token es válido y obtener información básica de la empresa.

**Headers:**
`X-Token: [TU_TOKEN]`

**Respuesta Exitosa (200 OK):**
```json
{
  "valid": true,
  "company_name": "Nombre de la Empresa",
  "org_id": "ID_DE_LA_ORGANIZACION"
}
```

## 2. Integraciones con Procesadores de Pago

El sistema Revenue-Recovery-OS está diseñado para integrarse con múltiples procesadores de pago a través de webhooks, lo que le permite reaccionar a eventos de pago fallidos y activar lógicas de recuperación. Aunque Stripe tiene una integración más explícita con validación de firma de webhook, la arquitectura permite la incorporación de otros procesadores mediante endpoints dedicados y un servicio genérico de recuperación.

### 2.1. Procesadores de Pago Soportados (Vía Webhooks)

El sistema incluye endpoints específicos para los siguientes procesadores de pago, lo que indica su preparación para manejar eventos de pago fallidos de cada uno:

*   **Stripe**: Integración principal para la gestión de pagos y suscripciones, con validación de firma de webhook para mayor seguridad.
*   **Adyen**: Orientado a empresas grandes, con un webhook dedicado para procesar notificaciones de eventos.
*   **PayPal / Braintree**: Soporte para plataformas de e-commerce, con un webhook para eventos como `subscription_charge_unsuccessful`.
*   **Checkout.com**: Enfocado en mercados de Europa y Asia, con un webhook para eventos como `payment_declined`.
*   **Mercado Pago**: Principal procesador para Latinoamérica, con un webhook para notificaciones de pago (`payment.created`, `payment.updated`). Requiere consulta adicional a la API de Mercado Pago para obtener detalles completos del pago.
*   **PayU**: Otro procesador relevante en Latinoamérica, con un webhook para estados de pago como `DECLINED`.
*   **Kushki / Niubiz**: Procesadores para Perú y países Andinos, con un webhook que maneja estados de transacción como `DECLINED`.

### 2.2. Almacenamiento Seguro de Claves API (Vault)

El sistema utiliza un `VaultService` para almacenar de forma segura las claves API de los diferentes procesadores de pago. Esto permite que el sistema sea agnóstico al procesador en cuanto a la gestión de credenciales.

**Endpoint:** `POST /api/v1/organization/vault/api-key`

Permite el envío seguro de claves API de procesadores de pago. Requiere validación por token.

**Cuerpo de la Solicitud (JSON):**

```json
{
  "processor": "stripe", // Puede ser "stripe", "adyen", "mercadopago", etc.
  "api_key": "sk_test_SU_CLAVE_AQUI"
}
```

**Seguridad:** La clave API se encripta utilizando el algoritmo Fernet (AES-256), garantizando seguridad bancaria para los datos sensibles.

## 3. Especificación de Endpoints por Pantalla

### 3.1. Dashboard

**Endpoint:** `GET /api/v1/dashboard/metrics`

Obtiene las métricas clave para mostrar en el panel de control. Requiere validación por token.

**Esquema de Respuesta (JSON):**

```json
{
  "recovered_amount": 1500.75,              // Dinero total recuperado
  "reduction_in_collection_days": 5.2,     // Reducción promedio en días de cobro
  "accounts_at_risk": 10,                  // Cuentas en riesgo de impago
  "monthly_recovered": 1200.50,            // Dinero recuperado este mes
  "recovery_rate": 85.5,                   // Tasa de éxito de recuperación (%)
  "active_recovery_campaigns": 3,          // Campañas de recuperación activas
  "message_summary": "¡Felicidades! Este mes recuperamos $1,200.50 USD que dabas por perdidos"
}
```

### 3.2. Branding

**Endpoint GET:** `GET /api/v1/organization/branding`

Recupera la configuración de branding actual de la organización. Requiere validación por token.

**Esquema de Respuesta (JSON):**

```json
{
  "logo_url": "https://ejemplo.com/mi-logo.png",
  "primary_color": "#3b82f6",
  "secondary_color": "#1e293b",
  "tone": "professional",
  "company_name": "Mi Empresa S.A."
}
```

**Endpoint POST:** `POST /api/v1/organization/branding`

Actualiza la configuración de branding de la organización. Requiere validación por token.

**Cuerpo de la Solicitud (JSON):**

```json
{
  "logo_url": "https://nueva-url.com/logo.png",
  "primary_color": "#FF0000",
  "secondary_color": "#00FF00",
  "tone": "friendly",
  "company_name": "Mi Empresa Renovada"
}
```

### 3.3. Webhooks de Procesadores de Pago

Estos endpoints están diseñados para recibir notificaciones de eventos de pago fallidos de los respectivos procesadores. Todos ellos activan una lógica genérica de recuperación (`process_generic_recovery`) que inicia reintentos inteligentes y campañas de dunning.

**Endpoint:** `POST /api/v1/webhooks/stripe`

Webhook para recibir eventos de Stripe, especialmente `invoice.payment_failed`.

**Headers:**
`Stripe-Signature: [FIRMA_DEL_WEBHOOK]` (requerido en producción)

**Cuerpo de la Solicitud (JSON):**
El payload completo del evento de Stripe. Ejemplo para `invoice.payment_failed`:
```json
{
  "id": "evt_12345",
  "object": "event",
  "type": "invoice.payment_failed",
  "data": {
    "object": {
      "id": "in_12345",
      "customer": "cus_abcde",
      "amount_due": 10000, // en centavos
      "currency": "usd",
      "metadata": {"org_id": "org_xyz"}
    }
  }
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "success",
  "message": "Payment failure logged, recovery logic queued"
}
```

**Endpoint:** `POST /api/v1/webhooks/processors/adyen`

Webhook para recibir notificaciones de Adyen, procesando eventos de autorización fallidos.

**Cuerpo de la Solicitud (JSON):**
El payload de notificación de Adyen. Ejemplo para una autorización fallida:
```json
{
  "notificationItems": [
    {
      "NotificationRequestItem": {
        "eventCode": "AUTHORISATION",
        "success": "false",
        "pspReference": "8815520104900001",
        "merchantReference": "INV-2023-001",
        "amount": {"value": 1000, "currency": "EUR"}
      }
    }
  ]
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "accepted"
}
```

**Endpoint:** `POST /api/v1/webhooks/processors/paypal-braintree`

Webhook para recibir eventos de PayPal/Braintree, como fallos en cargos de suscripción.

**Cuerpo de la Solicitud (JSON):**
El payload del evento de Braintree. Ejemplo para `subscription_charge_unsuccessful`:
```json
{
  "kind": "subscription_charge_unsuccessful",
  "subscription": {
    "id": "sub_123",
    "customer_id": "cust_456",
    "price": "50.00",
    "currency_iso_code": "USD"
  }
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "ok"
}
```

**Endpoint:** `POST /api/v1/webhooks/processors/checkout`

Webhook para recibir eventos de Checkout.com, como pagos declinados.

**Cuerpo de la Solicitud (JSON):**
El payload del evento de Checkout.com. Ejemplo para `payment_declined`:
```json
{
  "id": "evt_xyz",
  "type": "payment_declined",
  "data": {
    "id": "pay_abc",
    "reference": "INV-2023-002",
    "amount": 2000, // en unidades menores
    "currency": "GBP",
    "customer": {"id": "cus_789"}
  }
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "ok"
}
```

**Endpoint:** `POST /api/v1/webhooks/processors/mercadopago`

Webhook para recibir notificaciones de Mercado Pago, como la creación o actualización de pagos.

**Cuerpo de la Solicitud (JSON):**
El payload de notificación de Mercado Pago. Ejemplo para `payment.created`:
```json
{
  "id": "123456789",
  "live_mode": true,
  "type": "payment",
  "date_created": "2023-01-01T10:00:00.000-04:00",
  "application_id": 12345,
  "user_id": 67890,
  "version": 1,
  "api_version": "v1",
  "action": "payment.created",
  "data": {
    "id": "987654321"
  }
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "ok"
}
```

**Endpoint:** `POST /api/v1/webhooks/processors/payu`

Webhook para recibir notificaciones de PayU, especialmente para pagos declinados.

**Cuerpo de la Solicitud (JSON):**
El payload de notificación de PayU. Ejemplo para un pago declinado:
```json
{
  "test": false,
  "transaction_id": "abc-123",
  "state_pol": "6", // 6 = DECLINED
  "reference_sale": "INV-2023-003",
  "value": "75.00",
  "currency": "COP",
  "payer_id": "pay_111"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "ok"
}
```

**Endpoint:** `POST /api/v1/webhooks/processors/kushki-niubiz`

Webhook para recibir notificaciones de Kushki/Niubiz, como transacciones declinadas.

**Cuerpo de la Solicitud (JSON):**
El payload de notificación de Kushki/Niubiz. Ejemplo para una transacción declinada:
```json
{
  "transaction_id": "txn_xyz",
  "transaction_status": "DECLINED",
  "amount": 120.50,
  "currency": "PEN",
  "customer_id": "cus_222",
  "ticket_number": "TKT-2023-001"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "status": "ok"
}
```

## 4. Manejo de Errores

El API utiliza códigos de estado HTTP estándar:

| Código de Estado | Descripción |
| :--- | :--- |
| `200 OK` | Solicitud exitosa. |
| `401 Unauthorized` | Token inválido, ausente o expirado. |
| `404 Not Found` | Recurso no encontrado. |
| `500 Internal Server Error` | Error interno del servidor. |
| `503 Service Unavailable` | Conexión a la base de datos no disponible. |

---
**Nota:** Se ha eliminado el soporte para JWT y el flujo de Login/Registro interno en favor de la validación directa por token contra Firestore para facilitar la integración con interfaces externas.

**Autor:** Manus AI
