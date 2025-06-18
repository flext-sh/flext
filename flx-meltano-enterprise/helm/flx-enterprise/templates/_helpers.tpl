{{/*
Expand the name of the chart.
*/}}
{{- define "flx-enterprise.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "flx-enterprise.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "flx-enterprise.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "flx-enterprise.labels" -}}
helm.sh/chart: {{ include "flx-enterprise.chart" . }}
{{ include "flx-enterprise.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "flx-enterprise.selectorLabels" -}}
app.kubernetes.io/name: {{ include "flx-enterprise.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "flx-enterprise.serviceAccountName" -}}
{{- if .Values.security.serviceAccount.create }}
{{- default (include "flx-enterprise.fullname" .) .Values.security.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.security.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create PostgreSQL connection string
*/}}
{{- define "flx-enterprise.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
{{- $host := printf "%s-postgresql" (include "flx-enterprise.fullname" .) }}
{{- $port := "5432" }}
{{- $user := .Values.postgresql.auth.username }}
{{- $password := .Values.postgresql.auth.password }}
{{- $database := .Values.postgresql.auth.database }}
{{- printf "postgresql://%s:%s@%s:%s/%s" $user $password $host $port $database }}
{{- else }}
{{- required "Database URL must be provided when PostgreSQL is disabled" .Values.externalDatabase.url }}
{{- end }}
{{- end }}

{{/*
Create Redis connection string
*/}}
{{- define "flx-enterprise.redisUrl" -}}
{{- if .Values.redis.enabled }}
{{- $host := printf "%s-redis-master" (include "flx-enterprise.fullname" .) }}
{{- $port := "6379" }}
{{- $password := .Values.redis.auth.password }}
{{- printf "redis://:%s@%s:%s/0" $password $host $port }}
{{- else }}
{{- required "Redis URL must be provided when Redis is disabled" .Values.externalRedis.url }}
{{- end }}
{{- end }}
