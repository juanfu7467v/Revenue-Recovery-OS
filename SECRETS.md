
# 🔐 Guía de Configuración de Secretos para Revenue Recovery OS

Para asegurar el funcionamiento óptimo y seguro de **Revenue Recovery OS**, es imperativo configurar las variables de entorno (Secrets) detalladas a continuación. Estas variables deben ser gestionadas a través de su plataforma de despliegue predilecta, como **Fly.io**, **Railway** o **GitHub Actions**.

## 1. Infraestructura de Firebase y Firestore

El sistema depende fundamentalmente de Firebase para la persistencia de datos y la gestión de la autenticación. La siguiente tabla detalla las credenciales del **Service Account** necesarias para establecer una conexión segura con Firestore.

| Variable | Descripción | Ejemplo / Nota |
| :--- | :--- | :--- |
| `FIREBASE_PROJECT_ID` | Identificador único del proyecto en Firebase. | `mi-proyecto-recovery` |
| `FIREBASE_CLIENT_EMAIL` | Correo electrónico de la cuenta de servicio. | `firebase-adminsdk@...iam.gserviceaccount.com` |
| `FIREBASE_PRIVATE_KEY` | Clave privada completa del archivo JSON. | Debe incluir `-----BEGIN PRIVATE KEY-----` |
| `FIREBASE_TYPE` | Tipo de cuenta de servicio. | Siempre debe ser `service_account` |

## 2. Seguridad, Encriptación y Autenticación

La protección de los datos sensibles de los clientes, como las API Keys de los procesadores de pago, se realiza mediante una capa de encriptación simétrica en el **Vault**.

| Variable | Propósito | Recomendación |
| :--- | :--- | :--- |
| `ENCRYPTION_KEY` | Clave Fernet para encriptar tokens en el Vault. | Genérela con `cryptography.fernet.Fernet.generate_key()` |
| `SECRET_KEY` | Clave maestra para la firma de tokens JWT. | Use una cadena aleatoria de alta entropía. |
| `ALGORITHM` | Algoritmo de encriptación para JWT. | Por defecto se utiliza `HS256`. |

> **Nota Crítica:** La `ENCRYPTION_KEY` debe ser persistente. Si se modifica o se pierde, todos los datos actualmente encriptados en el Vault se volverán inaccesibles de forma permanente.

## 3. Integración con Procesadores de Pago

Para que el sistema pueda reaccionar a los eventos de pago fallidos y ejecutar reintentos automáticos, se requiere la configuración de los secretos de los procesadores activos.

| Procesador | Variable | Uso Principal |
| :--- | :--- | :--- |
| **Stripe** | `STRIPE_WEBHOOK_SECRET` | Validación de la firma de eventos entrantes. |
| **Stripe** | `STRIPE_SECRET_KEY` | Ejecución de cobros y gestión de suscripciones. |
| **Mercado Pago** | `MERCADOPAGO_ACCESS_TOKEN` | Interacción con la API de pagos en Latinoamérica. |

## 4. Canales de Comunicación y Dunning Multicanal

La recuperación de ingresos se apoya en una estrategia de comunicación proactiva. Estas variables permiten al sistema enviar notificaciones automáticas a través de diversos canales.

| Canal | Variable | Descripción |
| :--- | :--- | :--- |
| **Email** | `RESEND_API_KEY` | Token de acceso para el servicio de correos Resend. |
| **WhatsApp/SMS** | `TWILIO_ACCOUNT_SID` | Identificador de cuenta de Twilio. |
| **WhatsApp/SMS** | `TWILIO_AUTH_TOKEN` | Token de autenticación para la API de Twilio. |
| **WhatsApp/SMS** | `TWILIO_PHONE_NUMBER` | Número emisor configurado en su consola de Twilio. |

## 5. Variables de Entorno Adicionales

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `PORT` | Puerto de escucha para el servidor FastAPI. | `8080` |
| `DATABASE_URL` | URL de conexión para base de datos SQL opcional. | N/A |
| `DEBUG_MODE` | Habilita logs detallados para desarrollo. | `False` |

Al configurar estas variables, el sistema estará plenamente capacitado para realizar la **recuperación de pagos**, gestionar el **branding personalizado** y validar los **planes de suscripción** de los usuarios de manera automatizada.
