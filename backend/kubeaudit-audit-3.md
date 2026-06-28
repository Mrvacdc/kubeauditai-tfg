# Reporte de auditoría KubeAudit - Auditoría 3

**Fecha de generación:** 2026-06-23T22:17:07.502559+00:00

## 1. Información del clúster

- **Cluster ID:** 1
- **Nombre:** kubeaudit-kind-demo
- **Ambiente:** N/D
- **API Server:** N/D

## 2. Resumen de cumplimiento

- **Estado de auditoría:** completed
- **Total de controles:** 131
- **PASS:** 60
- **FAIL:** 15
- **WARN:** 56
- **Cumplimiento:** 45.8%

## 3. Recomendaciones por fuente y estado

- **deepseek / APPLIED:** 2
- **deepseek / DISMISSED:** 1
- **deepseek / PENDING:** 68
- **rule_engine / APPLIED:** 1
- **rule_engine / PENDING:** 70

## 4. Hallazgos FAIL/WARN principales

### 1.1.12 - FAIL

**Control:** Ensure that the etcd data directory ownership is set to etcd:etcd (Automated)

**Detalle:** Ensure that the etcd data directory ownership is set to etcd:etcd (Automated)

**Evidencia sanitizada:** {'audit': 'DATA_DIR=\'\'\nfor d in $(ps -ef | grep etcd | grep -- --data-dir | sed \'s%.*data-dir[= ]\\([^ ]*\\).*%\\1%\'); do\n  if test -d "$d"; then DATA_DIR="$d"; fi\ndone\nif ! test -d "$DATA_DIR"; then DATA_DIR=/var/lib/etcd/default.etcd; fi\nstat -c %U:%G "$DATA_DIR"\n', 'actual_value': 'root:root', 'expected_result': "'etcd:etcd' is present", 'reason': None}

**Hash de evidencia:** 881cfc7b3a88cb62177ec923c5bb1466b982ece70c39c19e3d16da801a5eab38

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.2.15 - FAIL

**Control:** Ensure that the --profiling argument is set to false (Automated)

**Detalle:** Ensure that the --profiling argument is set to false (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-apiserver | grep -v grep', 'actual_value': 'root         627     352  4 01:40 ?        00:07:44 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key --runtime-config=', 'expected_result': "'--profiling' is present", 'reason': None}

**Hash de evidencia:** 83b6170deb645902e0a6703f791f60e849e9bb6ab6edcfde3c4bdbdf7925bd2c

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.2.16 - FAIL

**Control:** Ensure that the --audit-log-path argument is set (Automated)

**Detalle:** Ensure that the --audit-log-path argument is set (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-apiserver | grep -v grep', 'actual_value': 'root         627     352  4 01:40 ?        00:07:44 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key --runtime-config=', 'expected_result': "'--audit-log-path' is present", 'reason': None}

**Hash de evidencia:** 72ce1b3fc3c76dcf80f756fe04a4036dc57e7d1294076e36572998dc395ba4cd

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.2.17 - FAIL

**Control:** Ensure that the --audit-log-maxage argument is set to 30 or as appropriate (Automated)

**Detalle:** Ensure that the --audit-log-maxage argument is set to 30 or as appropriate (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-apiserver | grep -v grep', 'actual_value': 'root         627     352  4 01:40 ?        00:07:44 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key --runtime-config=', 'expected_result': "'--audit-log-maxage' is present", 'reason': None}

**Hash de evidencia:** e206f4992f345186f53e3af69bfbdf1956cad1a83d3dfde8e457f89266853303

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.2.18 - FAIL

**Control:** Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate (Automated)

**Detalle:** Ensure that the --audit-log-maxbackup argument is set to 10 or as appropriate (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-apiserver | grep -v grep', 'actual_value': 'root         627     352  4 01:40 ?        00:07:44 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key --runtime-config=', 'expected_result': "'--audit-log-maxbackup' is present", 'reason': None}

**Hash de evidencia:** ffe7cfdacaf6ed0dd5e128bf8e816a9ce3f5004526053325738726beec85a731

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.2.19 - FAIL

**Control:** Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate (Automated)

**Detalle:** Ensure that the --audit-log-maxsize argument is set to 100 or as appropriate (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-apiserver | grep -v grep', 'actual_value': 'root         627     352  4 01:40 ?        00:07:44 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key --runtime-config=', 'expected_result': "'--audit-log-maxsize' is present", 'reason': None}

**Hash de evidencia:** 24636b800836f865113bfc462911f20f85843f535e60f7274e3da213c7e0ed41

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.2.30 - FAIL

**Control:** Ensure that the --service-account-extend-token-expiration parameter is set to false (Automated)

**Detalle:** Ensure that the --service-account-extend-token-expiration parameter is set to false (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-apiserver | grep -v grep', 'actual_value': 'root         627     352  4 01:40 ?        00:07:44 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key --runtime-config=', 'expected_result': "'--service-account-extend-token-expiration' is present", 'reason': None}

**Hash de evidencia:** e0d5cd4db520b867825b086bc9765399ae6a21e687ad5129d42453c38eb26573

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.2.5 - FAIL

**Control:** Ensure that the --kubelet-certificate-authority argument is set as appropriate (Automated)

**Detalle:** Ensure that the --kubelet-certificate-authority argument is set as appropriate (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-apiserver | grep -v grep', 'actual_value': 'root         627     352  4 01:40 ?        00:07:44 kube-apiserver --advertise-address=172.18.0.2 --allow-privileged=true --authorization-mode=Node,RBAC --client-ca-file=/etc/kubernetes/pki/ca.crt --enable-admission-plugins=NodeRestriction --enable-bootstrap-token-auth=true --etcd-cafile=/etc/kubernetes/pki/etcd/ca.crt --etcd-certfile=/etc/kubernetes/pki/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/pki/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --proxy-client-cert-file=/etc/kubernetes/pki/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/pki/front-proxy-client.key --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/pki/sa.pub --service-account-signing-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --tls-cert-file=/etc/kubernetes/pki/apiserver.crt --tls-private-key-file=/etc/kubernetes/pki/apiserver.key --runtime-config=', 'expected_result': "'--kubelet-certificate-authority' is present", 'reason': None}

**Hash de evidencia:** 5339959b1c09b83ab80c565492e4cab6939159a6c3384a2ed1986141af584710

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.3.2 - FAIL

**Control:** Ensure that the --profiling argument is set to false (Automated)

**Detalle:** Ensure that the --profiling argument is set to false (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-controller-manager | grep -v grep', 'actual_value': 'root         619     370  1 01:40 ?        00:03:20 kube-controller-manager --allocate-node-cidrs=true --authentication-kubeconfig=/etc/kubernetes/controller-manager.conf --authorization-kubeconfig=/etc/kubernetes/controller-manager.conf --bind-address=127.0.0.1 --client-ca-file=/etc/kubernetes/pki/ca.crt --cluster-cidr=10.244.0.0/16 --cluster-name=kubeaudit-demo --cluster-signing-cert-file=/etc/kubernetes/pki/ca.crt --cluster-signing-key-file=/etc/kubernetes/pki/ca.key --controllers=*,bootstrapsigner,tokencleaner --kubeconfig=/etc/kubernetes/controller-manager.conf --leader-elect=true --requestheader-client-ca-file=/etc/kubernetes/pki/front-proxy-ca.crt --root-ca-file=/etc/kubernetes/pki/ca.crt --service-account-private-key-file=/etc/kubernetes/pki/sa.key --service-cluster-ip-range=10.96.0.0/16 --use-service-account-credentials=true --enable-hostpath-provisioner=true', 'expected_result': "'--profiling' is present", 'reason': None}

**Hash de evidencia:** fa7b1f484c93043d68cb925ae851b95bf01a3bbbe1cf419ddec392c90cb47c87

**Detectado en:** 2026-06-22 04:38:26.979045+00:00

### 1.4.1 - FAIL

**Control:** Ensure that the --profiling argument is set to false (Automated)

**Detalle:** Ensure that the --profiling argument is set to false (Automated)

**Evidencia sanitizada:** {'audit': '/bin/ps -ef | grep kube-scheduler | grep -v grep', 'actual_value': 'root         577     317  0 01:40 ?        00:01:25 kube-scheduler --authentication-kubeconfig=/etc/kubernetes/scheduler.conf --authorization-kubeconfig=/etc/kubernetes/scheduler.conf --bind-address=127.0.0.1 --kubeconfig=/etc/kubernetes/scheduler.conf --leader-elect=true', 'expected_result': "'--profiling' is present", 'reason': None}

**Hash de evidencia:** 8632d560939d1c42d4922469807b48d2944e9410e268192a199f9d187dc73d7c

**Detectado en:** 2026-06-22 04:38:26.979045+00:00


## 5. Plan de remediación priorizado

**Total pendiente:** 138

- **HIGH / deepseek:** 63
- **HIGH / rule_engine:** 15
- **LOW / rule_engine:** 24
- **MEDIUM / deepseek:** 5
- **MEDIUM / rule_engine:** 31

### 1.1.9 - HIGH - deepseek

**Recomendación:** Remediación para CIS 1.1.9: Permisos de archivos de interfaz de red de contenedores (CNI)

Asegúrese de que los permisos de los archivos de configuración de la interfaz de red de contenedores (CNI) estén configurados en 600 o más restrictivos. Ejecute el siguiente comando en el nodo del plano de control: chmod 600 <ruta/a/los/archivos/cni>. Reemplace '<ruta/a/los/archivos/cni>' con la ruta real del directorio o archivos CNI (por ejemplo, /etc/cni/net.d/). Verifique que los archivos tengan permisos 600 utilizando: stat -c %a <ruta/al/archivo>.

Nota operacional:
1) Identifique la ubicación exacta de los archivos CNI en su clúster (por ejemplo, /etc/cni/net.d/ o /opt/cni/bin/). 2) Ejecute el comando chmod en todos los archivos dentro del directorio. 3) Verifique que no haya archivos con permisos incorrectos. 4) Si se utiliza Helm u otras herramientas de gestión, asegúrese de que las configuraciones persistentes no reviertan los permisos. 5) Reinicie los componentes del plano de control si es necesario para aplicar cambios de seguridad adicionales. 6) Este cambio es reversible; puede revertir los permisos ejecutando chmod con los valores anteriores.

### 1.2.11 - HIGH - deepseek

**Recomendación:** Habilitar el plugin de control de admisión AlwaysPullImages

Editar el archivo de especificación del pod del servidor API en /etc/kubernetes/manifests/kube-apiserver.yaml en el nodo de plano de control. Agregar 'AlwaysPullImages' al parámetro --enable-admission-plugins. Si ya existe una lista, agregarlo separado por comas. Luego, el kubelet reiniciará automáticamente el pod del API server.

Nota operacional:
Verifique que el parámetro --enable-admission-plugins contenga 'AlwaysPullImages' antes de aplicar el cambio. No modifique otros plugins existentes. Realice un backup del archivo original. Después de la modificación, verifique que el pod del API server se reinicie correctamente (kubectl get pods -n kube-system). Si hay múltiples nodos de plano de control, repita en cada uno. Esta acción es reversible eliminando la entrada del plugin.

### 1.2.15 - HIGH - deepseek

**Recomendación:** Deshabilitar profiling en API Server

Editar el archivo de especificación del pod del API server en /etc/kubernetes/manifests/kube-apiserver.yaml y asegurar que el argumento --profiling=false esté presente.

Nota operacional:
Verificar que el cambio sea correcto antes de aplicar. El API server se reiniciará automáticamente al modificar el manifiesto. Monitorear el estado del cluster después del cambio.

### 1.2.16 - HIGH - deepseek

**Recomendación:** Configurar la ruta del archivo de registro de auditoría del API Server

Editar el archivo de especificación del pod del API Server en /etc/kubernetes/manifests/kube-apiserver.yaml en el nodo del plano de control y agregar o modificar el argumento --audit-log-path con una ruta adecuada, por ejemplo, --audit-log-path=/var/log/apiserver/audit.log.

Nota operacional:
Realizar el cambio en cada nodo del plano de control. El kubelet recreará automáticamente el pod del API Server con la nueva configuración. Se recomienda notificar a los equipos de operaciones y verificar que los registros se estén escribiendo correctamente después del cambio.

### 1.2.17 - HIGH - deepseek

**Recomendación:** Remediación para CIS Control 1.2.17: Configurar --audit-log-maxage en el API Server

Editar el archivo de especificación del pod del API server en /etc/kubernetes/manifests/kube-apiserver.yaml en el nodo de control plane y agregar o modificar el argumento --audit-log-maxage a 30 (o un número de días apropiado según la política de retención de la organización). Por ejemplo: --audit-log-maxage=30. Luego, guardar el archivo. El kubelet detectará el cambio y reiniciará automáticamente el pod del API server. Verificar que el pod esté funcionando correctamente con kubectl get pods -n kube-system.

Nota operacional:
Asegúrese de que el disco donde se almacenan los registros de auditoría tenga suficiente espacio para 30 días de registros, considerando el volumen esperado. Monitoree el consumo de disco y ajuste el valor si es necesario. El cambio activa un reinicio automático del API server, lo que podría causar una breve interrupción; programe en ventana de mantenimiento si es necesario. Verifique que el argumento --audit-log-maxage esté correctamente escrito y que no haya conflictos con otros parámetros de auditoría.

### 1.2.19 - HIGH - deepseek

**Recomendación:** Establecer el tamaño máximo del archivo de auditoría (--audit-log-maxsize) a 100 MB o según lo apropiado

Editar el archivo de especificación del pod del API server en /etc/kubernetes/manifests/kube-apiserver.yaml en el nodo de control plane y establecer el parámetro --audit-log-maxsize a un tamaño apropiado en MB. Por ejemplo, para establecerlo a 100 MB, añadir o modificar: --audit-log-maxsize=100. Luego, el kubelet recreará automáticamente el pod del API server con la nueva configuración.

Nota operacional:
Antes de editar el manifiesto estático, verifique que el archivo exista y haga una copia de seguridad. Realice el cambio en todos los nodos de control plane. El cambio es inmediato; el kubelet detectará la modificación y reiniciará el contenedor del API server. Monitoree que el API server se reinicie correctamente y verifique los logs de auditoría. Si el valor actual es mayor a 100 MB, considere ajustarlo según la capacidad de almacenamiento y política de retención.

### 1.2.27 - HIGH - deepseek

**Recomendación:** Habilitar cifrado de datos en reposo en etcd mediante --encryption-provider-config

Configurar el archivo EncryptionConfig y agregar el argumento --encryption-provider-config al API server. Editar el archivo de especificación del pod del API server en /etc/kubernetes/manifests/kube-apiserver.yaml en el nodo control-plane y establecer el parámetro --encryption-provider-config con la ruta al archivo de configuración de cifrado. Por ejemplo: --encryption-provider-config=/etc/kubernetes/encryption-config.yaml. Asegurarse de que el archivo de configuración contenga un proveedor de cifrado (por ejemplo, aescbc) y que los recursos a cifrar incluyan secrets.

Nota operacional:
Antes de modificar el manifiesto, realizar una copia de seguridad del archivo original. Verificar que el archivo de configuración de cifrado esté correctamente formateado y que el proveedor de cifrado sea seguro (por ejemplo, aescbc con una clave AES de 256 bits generada de forma segura). La clave de cifrado debe almacenarse de manera segura (por ejemplo, en un gestor de secretos). Tras aplicar el cambio, el API server se reiniciará automáticamente; monitorear su estado con 'kubectl get pods -n kube-system'. Probar que los secrets se puedan crear y leer correctamente. Este cambio no afecta a los secrets existentes hasta que se vuelvan a escribir; se recomienda forzar la reescritura ejecutando 'kubectl get secrets --all-namespaces -o json | kubectl replace -f -'.

### 1.2.28 - HIGH - deepseek

**Recomendación:** Configurar proveedores de cifrado en el servidor API

Habilitar el cifrado en reposo para los datos almacenados en etcd configurando un archivo EncryptionConfig en el servidor API. Elegir un proveedor de cifrado como aescbc, kms o secretbox. Asegurarse de respaldar y proteger adecuadamente las claves de cifrado. La configuración se realiza mediante el flag '--encryption-provider-config' apuntando al archivo de configuración. Seguir la documentación oficial de Kubernetes para definir el archivo EncryptionConfig.

Nota operacional:
Antes de aplicar, realizar una copia de seguridad de etcd. Verificar que el proveedor de cifrado elegido esté disponible y sea compatible. Probar la configuración en un entorno de pruebas. Monitorear el rendimiento del servidor API tras el cambio. No compartir las claves de cifrado en repositorios o configuraciones no seguras.

### 1.2.29 - HIGH - deepseek

**Recomendación:** Asegurar que el Servidor API solo utilice cifrados criptográficos fuertes

Editar el archivo de especificación del pod del servidor API en /etc/kubernetes/manifests/kube-apiserver.yaml en el nodo plano de control y agregar o modificar el parámetro --tls-cipher-suites con la siguiente lista de cifrados fuertes: TLS_AES_128_GCM_SHA256,TLS_AES_256_GCM_SHA384,TLS_CHACHA20_POLY1305_SHA256,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305,TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305,TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256. Luego, guardar el archivo. El kubelet volverá a cargar el manifiesto y reiniciará el pod automáticamente.

Nota operacional:
Verificar que todos los clientes que se conectan al servidor API (kubectl, kubelet, controladores) soporten al menos uno de los cifrados configurados. Probar en un entorno de preproducción antes de aplicar en producción. Monitorear los logs del servidor API para detectar errores de handshake TLS después del cambio. Si algún cliente no puede conectarse, revisar la lista de cifrados e incluir los necesarios, manteniendo solo los seguros. La lista proporcionada cumple con las recomendaciones de CIS y es compatible con versiones modernas de Kubernetes y herramientas clientes.

### 1.2.3 - HIGH - deepseek

**Recomendación:** Configurar el plugin de admisión DenyServiceExternalIPs

Editar el archivo de especificación del pod del servidor API en el nodo de plano de control: /etc/kubernetes/manifests/kube-apiserver.yaml. Agregar el plugin 'DenyServiceExternalIPs' a la lista de plugins de admisión habilitados, usando la bandera --enable-admission-plugins=..., anexando 'DenyServiceExternalIPs' a los plugins existentes. Por ejemplo, si ya hay otros plugins, la línea quedaría: --enable-admission-plugins=NodeRestriction,DenyServiceExternalIPs. Guardar el archivo y esperar a que el kube-apiserver se reinicie automáticamente (unos minutos). Verificar que el plugin esté activo comprobando que los intentos de crear servicios con externalIPs sean rechazados.

Nota operacional:
Antes de aplicar, verificar que ningún servicio existente use externalIPs, ya que podrían verse afectados. Para identificarlos, ejecute: kubectl get svc --all-namespaces -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.externalIPs[*]}{"\n"}{end}'. Si hay servicios con externalIPs, reevalúe su necesidad y migre a alternativas como LoadBalancer o Ingress. El cambio en el archivo YAML provocará un reinicio automático del kube-apiserver; monitoree que el pod se recupere correctamente con: kubectl get pods -n kube-system | grep kube-apiserver. En caso de problemas, revertir el cambio editando nuevamente el archivo.


## 6. Nota metodológica

Este reporte fue generado a partir de los resultados almacenados por KubeAudit, incluyendo hallazgos CIS Kubernetes, recomendaciones generadas por motor local y/o proveedor de IA, y estados de remediación registrados en la plataforma.
