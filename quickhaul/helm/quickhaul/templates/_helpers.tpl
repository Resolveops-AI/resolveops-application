{{/*
Expand the name of the chart.
*/}}
{{- define "quickhaul.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "quickhaul.fullname" -}}
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
Create chart label.
*/}}
{{- define "quickhaul.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels applied to every resource.
*/}}
{{- define "quickhaul.labels" -}}
helm.sh/chart: {{ include "quickhaul.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{/*
Selector labels for a given component.
Usage: {{ include "quickhaul.selectorLabels" (dict "root" . "component" "auth-service") }}
*/}}
{{- define "quickhaul.selectorLabels" -}}
app.kubernetes.io/name: {{ include "quickhaul.name" .root }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{/*
Image reference helper — prepends global.imageRegistry when set.
Usage: {{ include "quickhaul.image" (dict "registry" .Values.global.imageRegistry "image" .Values.authService.image) }}
*/}}
{{- define "quickhaul.image" -}}
{{- $reg := .registry | default "" -}}
{{- if $reg -}}
{{- printf "%s/%s:%s" $reg .image.repository .image.tag -}}
{{- else -}}
{{- printf "%s:%s" .image.repository .image.tag -}}
{{- end -}}
{{- end }}

{{/*
Name of the shared ConfigMap.
*/}}
{{- define "quickhaul.configmapName" -}}
{{- printf "%s-config" (include "quickhaul.fullname" .) }}
{{- end }}

{{/*
Name of the shared Secret.
*/}}
{{- define "quickhaul.secretName" -}}
{{- printf "%s-secrets" (include "quickhaul.fullname" .) }}
{{- end }}

{{/*
MongoDB service hostname.
*/}}
{{- define "quickhaul.mongoHost" -}}
{{- printf "%s-mongodb" (include "quickhaul.fullname" .) }}
{{- end }}

{{/*
Redis service hostname.
*/}}
{{- define "quickhaul.redisHost" -}}
{{- printf "%s-redis" (include "quickhaul.fullname" .) }}
{{- end }}
