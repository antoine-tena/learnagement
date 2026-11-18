// Composant de la liste des compétences
// Affiche la liste des compétences d'une filière
// Props:
// - infosCompetences: Tableau des informations des compétences
// - setIdCompetenceClicked: Fonction pour mettre à jour la compétence sélectionnée
// Composants importés:

import React, {useEffect, useState} from "react";

/**
 * Composant de la liste des compétences
 * Affiche la liste des compétences d'une filière
 *
 * @param {infosCompetence[]} infosCompetences - Tableau des informations des compétences
 * @param {Function} setIdCompetenceClicked - Fonction pour mettre à jour la compétence sélectionnée
 * @returns {JSX.Element} Composant React
 */
export default function ListCompetences({infosCompetences, setIdCompetenceClicked}:{infosCompetences: infosCompetence[], setIdCompetenceClicked: (id_competence: number) => void}){
    // La compétence cliquée ne vaut que pour la liste où elle l'a été ; sinon, la première
    const [clicked, setClicked] = useState<{competences: infosCompetence[], id_competence: number} | null>(null)
    const competenceClicked = clicked?.competences === infosCompetences
        ? clicked.id_competence
        : (infosCompetences[0]?.id_competence ?? -1)

    useEffect(() => {
        if (infosCompetences.length > 0){
            setIdCompetenceClicked(infosCompetences[0].id_competence)
        }
    }, [infosCompetences]);

    return(
        <div className={"mb-8"}>
            <h4>Compétences de la filière</h4>
            <div className={"w-full flex justify-center mb-8"}>
                <p className={"w-4/5 border-t border-gray-300"}></p>
            </div>

            {infosCompetences.length > 0 ?
                <div className={"flex justify-around"}>
                    {infosCompetences.map((competence:infosCompetence) => (
                        <div key={competence.id_competence} className={`w-60 h-20 px-2 flex items-center rounded-lg text-white cursor-pointer
                            ${competenceClicked === competence.id_competence ? 'bg-usmb-blue' : 'bg-usmb-cyan'}`}

                             onClick={() => {
                                 setIdCompetenceClicked(competence.id_competence)
                                 setClicked({competences: infosCompetences, id_competence: competence.id_competence})
                             }}
                        >
                            <p className={"font-semibold text-base/5"}>{competence.libelle_competence}</p>
                        </div>
                    ))}
                </div>
                :
                <p>Pas d’informations sur les compétences pour cette filière</p>}
            <div className={"w-full flex justify-center mt-8"}>
                <p className={"w-4/5 border-t border-gray-300"}></p>
            </div>
        </div>
    )
}
