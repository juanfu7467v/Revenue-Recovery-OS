# Documentación Técnica del API para el Panel de Control de Revenue-Recovery-OS

Esta documentación detalla los endpoints del API necesarios para el desarrollo de la interfaz de usuario del Panel de Control de Revenue-Recovery-OS. Se enfoca en el nuevo sistema de validación por token, la especificación de endpoints por pantalla, el manejo seguro de claves API y la gestión de webhooks.

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

## 2. Especificación de Endpoints por Pantalla

### 2.1. Dashboard

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

### 2.2. Branding

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

### 2.3. Vault (Almacenamiento Seguro de Claves API)

**Endpoint:** `POST /api/v1/organization/vault/api-key`

Permite el envío seguro de claves API de procesadores de pago. Requiere validación por token.

**Cuerpo de la Solicitud (JSON):**

```json
{
  "processor": "stripe",
  "api_key": "sk_test_SU_CLAVE_AQUI"
}
```

**Seguridad:** La clave API se encripta utilizando el algoritmo Fernet (AES-256), garantizando seguridad bancaria para los datos sensibles.

## 3. Manejo de Errores

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
