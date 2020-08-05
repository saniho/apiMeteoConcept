# apimetconcept


cet api permet de ce connecter à api.meteo-concept.com et recuperer des informations telque la prevision de la nuit à venir

pour l'utiliser, il suffit d'ajouter le sensor suivant : 

```yaml
- platform: apiMeteoConcept
  code: <code de la ville>
  token: <votre token>
```