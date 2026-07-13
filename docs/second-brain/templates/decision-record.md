---
type: decision
status: <% tp.system.suggester(["Propuesta", "Aceptada", "Rechazada", "Superada"], ["Propuesta", "Aceptada", "Rechazada", "Superada"]) %>
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [decision]
---

# <% tp.system.prompt("Título de la decisión") %>

## Contexto

## Decisión

## Consecuencias
