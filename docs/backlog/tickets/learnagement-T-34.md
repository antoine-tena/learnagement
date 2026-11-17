# T-34 · Plus de JWT dans les URL
- **Type**: bug
- **Priority**: 🟠 important
- **Status**: in progress — fix/front-auth-secrets
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: @antoine-tena · **Due**: —
- **Origin**: revue de l'architecture

Le jeton ne passe plus par l'URL : le PHP pose un cookie `lnm_token` (`HttpOnly`, `SameSite=Strict`,
`Secure` en HTTPS), que Dash lit sur le même hôte ; Next ne lisait pas `?jwt_token` et ne le reçoit
plus. `nextjs.php` force encore `http`, mais seule la connexion de Next y transite désormais.

- [ ] Vérifier sur une instance lancée, en HTTP puis en HTTPS : connexion, passage du PHP à Dash,
  navigation entre les pages de Dash, déconnexion (code modifié, pas encore lancé).
- [x] Transmettre l'authentification autrement : cookie `HttpOnly` et `Secure` sur un même domaine.
- [ ] Servir Next en HTTPS.
