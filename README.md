# Revenue-Recovery-OS: Cashflow Recovery API (Producción)

## Infraestructura Financiera de Recuperación de Liquidez

**Revenue-Recovery-OS** es una plataforma diseñada para la recuperación automatizada de ingresos perdidos por pagos fallidos. Arquitectura **no custodia**, **escalable** y **segura**.

---

## 🚀 Nuevas Mejoras: Expansión Global de Procesadores

Hemos transformado el sistema en una solución global compatible con múltiples procesadores de pago, permitiendo escalar a nivel internacional y dominar mercados clave como Latinoamérica.

### 🌍 Integración Internacional (Empresas Grandes)
*   **Adyen:** Ideal para empresas de gran escala (ej. Uber, Netflix).
*   **PayPal (Braintree):** Estándar en e-commerce y suscripciones globales.
*   **Checkout.com:** Tecnología moderna con fuerte presencia en Europa y Asia.

### 🌎 Enfoque en Latinoamérica (Mercado Clave)
*   **Mercado Pago:** Líder indiscutible en la región.
*   **PayU:** Amplia adopción para pagos recurrentes en Latam.
*   **Kushki / Niubiz:** Soluciones estratégicas para Perú y países andinos.

---

## 🛠️ Nuevos Endpoints de Webhooks
Se han habilitado rutas modulares para recibir notificaciones de fallos de pago de los nuevos procesadores:
*   `POST /api/v1/webhooks/processors/adyen`
*   `POST /api/v1/webhooks/processors/paypal-braintree`
*   `POST /api/v1/webhooks/processors/checkout`
*   `POST /api/v1/webhooks/processors/mercadopago`
*   `POST /api/v1/webhooks/processors/payu`
*   `POST /api/v1/webhooks/processors/kushki-niubiz`

---

## 🎨 Funcionalidades de Marca Blanca y Dashboard
*   **Personalización Avanzada:** Editor de marca (logo, colores, tono) para comunicaciones de cobro.
*   **Dashboard de "Dinero Recuperado":** Métricas en tiempo real sobre el impacto económico del sistema.
*   **Prevención Proactiva (Pre-Dunning):** Notificaciones automáticas para tarjetas próximas a vencer.

---

## Implementación Técnica de Producción

### 1. Seguridad (Validación por Token)
*   **Capa de Validación:** Se ha eliminado la lógica de registro y login interna. El sistema ahora valida cada petición mediante un token enviado en el header `X-Token`.
*   **Verificación Firestore:** Los tokens se validan directamente contra la colección `empresas` en Firestore (campo `token`).
*   **Vault (AES-256):** Almacenamiento encriptado de API Keys de todos los procesadores.

### 2. Base de Datos Firestore (Estructura)
*   **`empresas`**: Colección principal para validación de acceso y tokens.
*   `organizations`: Perfiles de clientes y configuración de branding.
*   `vault`: Almacén seguro de credenciales.
*   `recovery_events`: Auditoría de webhooks recibidos.
*   `recovery_logs`: Seguimiento detallado de facturas en recuperación por procesador.

### 3. Arquitectura Modular
El sistema utiliza una lógica de recuperación genérica (`process_generic_recovery`) que permite integrar nuevos procesadores sin afectar la estabilidad de los existentes, garantizando que el núcleo del negocio permanezca intacto.

---

## Guía de Despliegue en Fly.io

1.  **Configurar Secretos:** `ENCRYPTION_KEY`, `STRIPE_WEBHOOK_SECRET` y credenciales de Firebase.
2.  **Desplegar:** `fly deploy`.

---
**Autor:** Inge. Juan Carlos 
**Estado:** Global, Escalable y Listo para Producción
