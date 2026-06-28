# KubeAudit

KubeAudit es una aplicación web orientada a la gestión de auditorías de cumplimiento del CIS Kubernetes Benchmark en clústeres Kubernetes. El prototipo permite registrar un clúster objetivo, validar conectividad, ejecutar o procesar resultados de kube-bench, almacenar auditorías históricas, visualizar hallazgos y generar recomendaciones técnicas de remediación mediante inteligencia artificial previa sanitización de datos sensibles.

## Contexto del proyecto

Este repositorio forma parte del prototipo desarrollado para un Trabajo Final de Grado en Seguridad Informática. La solución busca transformar un proceso de auditoría manual y esporádico en un flujo más automatizado, trazable y orientado a la mejora continua del hardening de infraestructuras Kubernetes.

## Arquitectura demo

La arquitectura de demostración se implementa sobre AWS con un enfoque de bajo costo.

```text
Usuario
  |
  | HTTPS
  v
Route53: marcosvillegas.dev
  |
  | kubeauditai.marcosvillegas.dev
  v
EC2 Instance
  |
  |-- Caddy
  |-- React frontend static files
  |-- FastAPI backend
  |
  v
Amazon RDS PostgreSQL
  |
  v
Historial de auditorías, hallazgos y recomendaciones

FastAPI backend
  |
  | kubeconfig / ServiceAccount restringido
  v
Clúster Kubernetes externo
  |
  |-- kube-bench Job/CronJob
  |-- Resultados PASS / FAIL / WARN
```

La aplicación KubeAudit no se ejecuta dentro del clúster auditado. Se despliega como una aplicación web tradicional sobre EC2 y se conecta a un clúster Kubernetes externo mediante credenciales restringidas.

## Stack tecnológico

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL
* JWT
* bcrypt
* Kubernetes Python Client

### Frontend

* React
* TypeScript
* Vite
* Axios
* React Router

### Infraestructura demo

* Amazon EC2
* Amazon RDS PostgreSQL
* Route53
* Caddy o Nginx
* HTTPS
* Clúster Kubernetes externo

### Auditoría

* kube-bench
* Procesamiento de resultados PASS, FAIL y WARN
* Registro histórico de auditorías
* Visualización de cumplimiento

### Inteligencia artificial

* Generación de recomendaciones de remediación
* Sanitización previa de datos
* Bloqueo de secretos, tokens, certificados, contraseñas y kubeconfigs
* Revisión humana de recomendaciones generadas

## Alcance MVP

El prototipo inicial incluye:

1. Login.
2. Registro de clúster Kubernetes.
3. Validación de conexión contra Kubernetes API.
4. Ejecución o carga de resultados kube-bench.
5. Procesamiento de controles PASS, FAIL y WARN.
6. Persistencia histórica en PostgreSQL.
7. Consulta de auditorías.
8. Detalle de hallazgos.
9. Dashboard de cumplimiento.
10. Generación de recomendaciones con IA previa sanitización de datos.

## Variables de entorno

El backend utiliza variables definidas en:

```text
backend/.env.example
```

El frontend utiliza variables definidas en:

```text
frontend/.env.example
```

## Dominio público

```text
https://kubeauditai.marcosvillegas.dev
```

El dominio será gestionado mediante Route53 y apuntará a la instancia EC2 donde se desplegará la aplicación.

## Estado del proyecto


