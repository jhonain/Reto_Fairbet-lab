# ADR 0001: Estructura del Proyecto FairBet Lab

## Contexto
Necesitamos organizar el código de una plataforma de apuestas educativa 
con múltiples dominios: usuarios, wallet, apuestas, juego responsable, 
tiempo real, auditoría y operación.

## Opciones consideradas

### Opción A: Monolito con apps Django tradicionales
- **Pros:** Simple, bien documentado, fácil de desplegar
- **Contras:** Puede crecer desordenado si no se respeta la separación

### Opción B: Microservicios (APIs separadas)
- **Pros:** Escalabilidad independiente, equipos autónomos
- **Contras:** Overhead para un proyecto académico, complejidad de red

### Opción C: Monolito modular con apps Django bien delimitadas (ELEGIDA)
- **Pros:** Balance entre orden y simplicidad, permite TDD por app, 
  facilita la evaluación de cobertura por módulo
- **Contras:** Requiere disciplina para no crear dependencias circulares

## Decisión
Usar monolito Django con apps independientes por dominio, siguiendo 
dependencias unidireccionales: `users` → `wallet` → `betting`, con 
`audit` como servicio transversal.

## Consecuencias
- Fácil de testear por app
- Riesgo de dependencias circulares → mitigado con revisiones de código
- Escalable a microservicios si se mantiene la separación de servicios