<?php

/*
 * Réglages propres à Learnagement, lus après la configuration de l'image
 * (/etc/phpmyadmin/config.inc.php, qui inclut ce fichier en dernier).
 * Ce fichier ne doit jamais inclure config.inc.php : l'inclusion tournerait en boucle.
 */

/* Clés étrangères affichées par leur valeur (K) ou par leur colonne d'affichage (D) */
$relationalDisplay = getenv('RELATIONAL_DISPLAY');
if ($relationalDisplay !== false) {
    $cfg['RelationalDisplay'] = $relationalDisplay;
}
