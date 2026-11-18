import { withAuth } from "next-auth/middleware"

export default withAuth({
    pages: {
        signIn: "/connection",
    },
})

export const config = {
    matcher: [
        //"/homepage:path*",
        //"/modules:path*",
        // Protège tout sauf : health, assets Next, favicon, et l'activation d'un compte (la personne
        // n'a pas encore de mot de passe : la page et l'envoi de son formulaire)
        "/((?!health|_next/static|_next/image|favicon.ico|activateAccount|api/proxy/account-activation/confirm).*)"
    ],
}
