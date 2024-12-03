{{- define "testAppLabels" -}}
app: python-app-{{ .Values.testColor }}
{{- end -}}

{{- define "liveAppLabels" -}}
app: python-app-{{ .Values.liveColor }}
{{- end -}}
