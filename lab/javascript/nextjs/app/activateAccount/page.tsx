"use client"

import React, {Suspense, useState} from "react";
import Link from "next/link";
import {useSearchParams} from "next/navigation";
import axios from "axios";

import AlertBox from "../indicators/alertBox";

const PASSWORD_MIN_LENGTH = 12

function ActivationForm() {
    /* Le lien d'activation porte le jeton ; le mot de passe part en clair sur HTTPS, l'API le hache */
    const token = useSearchParams().get('token') ?? ''
    const [pwd, setPwd] = useState('')
    const [confirmation, setConfirmation] = useState('')
    const [message, setMessage] = useState<string | undefined>(undefined)
    const [isActivated, setIsActivated] = useState(false)

    async function activate(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (pwd.length < PASSWORD_MIN_LENGTH) {
            setMessage(`Le mot de passe doit faire au moins ${PASSWORD_MIN_LENGTH} caractères.`)
            return
        }
        if (pwd !== confirmation) {
            setMessage("Les deux mots de passe diffèrent.")
            return
        }
        try {
            await axios.post('/api/proxy/account-activation/confirm', {token, password: pwd},
                {headers: {"Content-Type": "application/json"}})
            setIsActivated(true)
            setMessage(undefined)
        } catch {
            setMessage("Lien d'activation invalide ou expiré : demandez-en un nouveau.")
        }
    }

    if (!token) {
        return <p>Ouvrez le lien d&apos;activation reçu de l&apos;administration.</p>
    }
    if (isActivated) {
        return <AlertBox text="Compte activé : vous pouvez vous connecter." color={"bg-usmb-green"}/>
    }
    return (
        <>
            {message && <AlertBox text={message} color={"bg-usmb-red"}/>}
            <form className={"flex flex-col gap-2"} method='post' onSubmit={activate}>
                <label htmlFor="pwd">Mot de passe</label>
                <input type="password" id="pwd" name="password" autoComplete="new-password" required={true}
                       minLength={PASSWORD_MIN_LENGTH} onChange={e => setPwd(e.target.value)}/>
                <label htmlFor="confirmation">Confirmation</label>
                <input type="password" id="confirmation" name="confirmation" autoComplete="new-password"
                       required={true} onChange={e => setConfirmation(e.target.value)}/>
                <button type="submit">Activer mon compte</button>
            </form>
        </>
    )
}

export default function ActivateAccount() {
    /* Page permettant d'activer son compte */
    return (
        <main className={"h-screen flex flex-col items-center justify-center"}>
            <div className={"flex flex-col items-center justify-around gap-4 p-4 shadow-lg"}>
                <Suspense>
                    <ActivationForm/>
                </Suspense>
                <Link href={"/connection"} className={"button-second"}>Retour</Link>
            </div>
        </main>
    );
}
