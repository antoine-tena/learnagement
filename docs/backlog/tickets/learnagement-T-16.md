# T-16 · Le mot de passe n'est plus haché dans le navigateur
- **Type**: bug
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: lecture de `frontend/app/activateAccount/page.tsx`

La page d'activation hache le mot de passe avec `bcryptjs` côté client puis envoie le hash : le
hash devient le secret, et le serveur ne contrôle ni le coût ni le sel. Envoyer le mot de passe
en HTTPS, hacher dans l'API (`pwdlib`).
