<?php
// Les mots de passe ne se gèrent plus depuis le front : l'inscription renvoie vers la connexion.
$t->router->redirect('login');
