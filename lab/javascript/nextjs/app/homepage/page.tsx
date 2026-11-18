"use client"

import axios from "axios";
import {useSession} from "next-auth/react";
import {useListModulesStore} from "@/app/store/useListModulesStore";
import SideMenu from "@/app/homepage/sideMenu"
import Homepage from "@/app/homepage/homepage";
import {Suspense, useEffect} from "react";
import Loader from "@/app/indicators/loading";

export default function Home() {
    const {data: session} = useSession()
    const {charged, setListModules, setCharged} = useListModulesStore()

    useEffect(() => {
        if (session && !charged){
            axios.get("/api/proxy/enseignant/" + session.user.id + "/module_responsabilities")
                .then(response => {
                    setListModules(response.data)
                    setCharged(true) // Permet de charger une seule fois ListModules, quand l'utilisateur se connecte pour la première fois
                })
        }
    }, [session]);

    return (
        <>
            <main className={"h-screen grid grid-cols-4"}>
                <Suspense>
                    <SideMenu />
                </Suspense>
                <div className={"col-span-3 overflow-y-auto"}>
                    <Homepage />
                </div>
          </main>
      </>
    );
}
