"use client"

import React, {useEffect, useState} from "react";
import Link from "next/link";
import bcrypt from 'bcryptjs';

import AlertBox from "../indicators/alertBox";

export default function ActivateAccount() {
    /* Page permettant d'activer son compte */

    const [pwd, setPwd] = useState('')
    const [hash, setHash] = useState('')
    const [resCopy, setResCopy] = useState(false)
    const [wantCopy, setWantCopy] = useState(false) // Permet de savoir si le bouton est cliqué

    useEffect(() => { /* Gère l'affichage du message 'copié' */
        if (!wantCopy) return;
        const timer = setTimeout(() => {
            setWantCopy(false); // Masque le message après 2 secondes ; un nouveau clic le réaffiche
        }, 2000);

        // Nettoyer le timer lorsqu'on quitte le composant pour éviter les fuites de mémoire
        return () => clearTimeout(timer);
    }, [wantCopy]);

    async function hashPassword(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault()
        const form = event.currentTarget

        try {
            setHash(await bcrypt.hash(pwd, 10))
        } catch {
            setHash("Erreur hashage")
        }
        form.reset()
    }

    async function copyHash(){
        setWantCopy(true);
        if (hash != ''){
            try{
                await navigator.clipboard.writeText(hash)
                setResCopy(true)
            }catch{
                setResCopy(false)
            }
        }

    }

    return (
        <main className={"h-screen flex flex-col items-center justify-center"}>
            {(resCopy && wantCopy) && <AlertBox text="Copié !" color={"bg-usmb-green"}/>}
            {(!resCopy && wantCopy) && <AlertBox text="Erreur !" color={"bg-usmb-red"}/>}
            {(hash == "Erreur hashage") &&  <AlertBox text="Erreur de hashage !" color={"bg-usmb-red"}/>}

            <div className={"flex flex-col items-center justify-around gap-4 p-4 shadow-lg"}>
                <p>
                    To activate (or change your password of) your account,<br/>
                    send the hash of your password to Learnagement admin.<br/>
                    WARNING! Communications are not crypted, do not use a main password.
                </p>
                <form className={"flex gap-2"} method='post' onSubmit={hashPassword}>
                    <input type="password" id="pwd" name="password" required={true} onChange={e => setPwd(e.target.value)}/>
                    <button type="submit" value="hash">hash</button>
                </form>
                {(hash != "Erreur hashage" && pwd != '' ) && hash}
                <div className={"flex items-center gap-5"}>
                    <button value="copy" onClick={copyHash}>Copier</button>
                    <Link href={"/connection"} className={"button-second"}>Retour</Link>
                </div>
            </div>
        </main>
    );
}
