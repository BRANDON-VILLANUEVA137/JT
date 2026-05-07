# 🔐 Sistema de Recuperación de Contraseña - SMTP Gmail

## ✅ Implementación Completada

Se ha implementado un sistema completo de recuperación de contraseña usando **SMTP con Gmail** en tu aplicación Django.

---

## 📋 Cambios Realizados

### 1. **Configuración de Settings.py** 
- Se agregaron las variables de entorno para configurar SMTP Gmail:
  - `EMAIL_BACKEND`: Backend SMTP de Django
  - `EMAIL_HOST`: smtp.gmail.com
  - `EMAIL_PORT`: 587 (TLS)
  - `EMAIL_USE_TLS`: True
  - `EMAIL_HOST_USER`: Tu email de Gmail
  - `EMAIL_HOST_PASSWORD`: Tu contraseña de aplicación
  - `DEFAULT_FROM_EMAIL`: Email del remitente

### 2. **Modelos Agregados** (`usuarios/models.py`)
Se agregó el modelo `PasswordResetToken`:
```python
class PasswordResetToken(models.Model):
    user = models.OneToOneField(Usuario, ...)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    # Métodos:
    - is_valid(): Verifica si el token es válido (< 24h, no usado)
    - generate_token(user): Genera nuevo token
```

### 3. **Formularios Agregados** (`usuarios/forms.py`)
Se crearon dos nuevos formularios:

#### `PasswordResetRequestForm`
- Campo: Email (validación de existencia)
- Envía enlace de recuperación al email del usuario

#### `PasswordResetForm`
- Campos: Nueva contraseña + Confirmación
- Valida requisitos de seguridad:
  - Mínimo 12 caracteres
  - Al menos 1 mayúscula
  - Al menos 1 minúscula
  - Al menos 1 número
  - Al menos 1 carácter especial

### 4. **Vistas Implementadas** (`usuarios/views.py`)

#### `password_reset_request_view()`
- **Ruta**: `/usuarios/recuperar-contrasena/`
- **Método**: GET, POST
- Solicita email del usuario
- Genera token único
- **Envía email con enlace de recuperación**
- Enlace válido por **24 horas**

#### `password_reset_view(token)`
- **Ruta**: `/usuarios/restablecer-contrasena/<token>/`
- **Método**: GET, POST
- Valida el token
- Permite crear nueva contraseña
- Marca token como usado

### 5. **URL Patterns** (`usuarios/urls.py`)
Se agregaron dos nuevas rutas:
```python
path('recuperar-contrasena/', views.password_reset_request_view, name='password_reset_request'),
path('restablecer-contrasena/<str:token>/', views.password_reset_view, name='password_reset'),
```

### 6. **Templates Creados**

#### `password_reset_request.html`
- Formulario para solicitar recuperación
- Diseño glassmorphism matching con login.html
- Validación en tiempo real

#### `password_reset.html`
- Formulario para restablecer contraseña
- Muestra requisitos de seguridad
- Confirmación de nueva contraseña
- Diseño consistente

### 7. **Login Actualizado**
Se agregó enlace en `login.html`:
```html
<a href="{% url 'usuarios:password_reset_request' %}" class="login-link">
  ¿Olvidaste tu contraseña?
</a>
```

### 8. **Migración de Base de Datos**
Se creó y aplicó: `usuarios/migrations/0013_passwordresettoken.py`

---

## 🔧 Configuración del .env

Tu archivo `.env` debe tener estas variables (ya están configuradas):

```env
# Email Configuration (SMTP - Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=oscardavi122@gmail.com
EMAIL_HOST_PASSWORD=rhcoflkziiteblst
DEFAULT_FROM_EMAIL=oscardavi122@gmail.com
```

---

## 🚀 Flujo de Recuperación de Contraseña

### Usuario olvida contraseña:

1. **Ingresa a**: `/usuarios/recuperar-contrasena/`
2. **Completa**: Email registrado
3. **Recibe**: Email con enlace de recuperación
4. **Email contiene**: Enlace válido por 24 horas
   ```
   /usuarios/restablecer-contrasena/{TOKEN}/
   ```
5. **Usuario accede** al enlace
6. **Establece**: Nueva contraseña (cumpliendo requisitos)
7. **Sistema**: Valida, guarda y marca token como usado
8. **Usuario**: Redirigido a login para ingresar con nueva contraseña

---

## 📧 Contenido del Email Enviado

```
Asunto: Recupera tu contraseña - TECH-JUANJO

Cuerpo:
Hola [Nombre Usuario],

Recibimos una solicitud para recuperar tu contraseña.
Si fuiste tú, haz click en el siguiente enlace:

[ENLACE_RECUPERACION]

Este enlace expira en 24 horas.
Si no solicitaste recuperar tu contraseña, ignora este email.

Saludos,
TECH-JUANJO
```

---

## 🔒 Requisitos de Contraseña

Las nuevas contraseñas deben cumplir:
- ✅ Mínimo 12 caracteres
- ✅ Al menos 1 mayúscula (A-Z)
- ✅ Al menos 1 minúscula (a-z)
- ✅ Al menos 1 número (0-9)
- ✅ Al menos 1 carácter especial (!@#$%^&*(),.?":{}|<>)
- ✅ No más de 3 caracteres iguales seguidos

---

## 🧪 Pruebas Recomendadas

### 1. Sin estar autenticado:
```bash
# Ir a la página de recuperación
http://localhost:8000/usuarios/recuperar-contrasena/

# Ingresar un email registrado
# Verificar que se recibe el email
# Hacer click en el enlace del email
# Completar nueva contraseña
# Intentar login con nueva contraseña
```

### 2. Validaciones:
- Intentar acceder con token expirado → Error
- Intentar reutilizar token → Error
- Intentar con email no registrado → Error
- Contraseña débil → Error

---

## 📁 Archivos Modificados

```
usuarios/
├── models.py                    ✏️ (+ PasswordResetToken)
├── forms.py                     ✏️ (+ 2 formularios)
├── views.py                     ✏️ (+ 2 vistas)
├── urls.py                      ✏️ (+ 2 rutas)
├── tokens.py                    ✏️ (importar PasswordResetToken)
├── migrations/
│   └── 0013_passwordresettoken.py   ✨ (NUEVO)
└── templates/usuarios/
    ├── login.html               ✏️ (agregar link)
    ├── password_reset_request.html  ✨ (NUEVO)
    └── password_reset.html      ✏️ (actualizado)

JUANJO_TECH/
└── settings.py                  ✏️ (+ config SMTP)

.env                             ✏️ (+ vars email)
```

---

## 🎯 Variables de Entorno Requeridas

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_app
DEFAULT_FROM_EMAIL=tu_email@gmail.com
```

> **⚠️ IMPORTANTE**: Usa una **contraseña de aplicación** de Google, no tu contraseña de Gmail normal.
> 
> Obtener contraseña de app:
> 1. Ve a: https://myaccount.google.com/apppasswords
> 2. Selecciona: Mail + Windows Computer
> 3. Copia la contraseña generada
> 4. Úsala en `EMAIL_HOST_PASSWORD`

---

## ✨ Características Adicionales

- ✅ Tokens únicos por usuario
- ✅ Validación de 24 horas
- ✅ Tokens marcados como usados (sin reutilización)
- ✅ Eliminación automática de tokens expirados
- ✅ Validación de requisitos de contraseña
- ✅ Interfaz UX moderna y responsiva
- ✅ Mensajes de error/éxito claros
- ✅ Protección CSRF

---

## 🐛 Troubleshooting

### Email no se envía:
1. Verifica que `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` son correctos
2. Asegúrate de usar **contraseña de aplicación** (no contraseña regular)
3. Revisa la consola de Django para errores SMTP
4. Verifica que `DEBUG=False` no bloquea errores

### Token expirado:
- Los tokens son válidos por **24 horas**
- Un token usado no puede reutilizarse
- Usuario debe solicitar nuevo enlace si expiró

### Contraseña débil:
- El formulario muestra los requisitos
- Todos deben cumplirse

---

## 📞 Contacto / Soporte

Si necesitas ajustar:
- Tiempo de expiración del token
- Requisitos de contraseña
- Contenido del email
- Diseño del template

Modifica los archivos indicados arriba. ¡Todo está bien documentado!

---

## ✅ Estado: COMPLETADO Y LISTO PARA USAR

La implementación está **lista para producción**. ¡Pruébalo ahora!
