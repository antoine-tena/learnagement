<?php
// Relaie la création d'un module à l'API (POST /modules), statut et message d'erreur compris.
header('Content-Type: application/json');
$body = file_get_contents('php://input');

if (json_decode($body, true)) {
    $token = $user["jwt_token"];
    $response = forwardToBackend("modules", "POST", $body, 'application/json', ["Authorization: Bearer $token"]);
    if ($response['status'] === 0) {
        http_response_code(502);
        echo json_encode(["detail" => "API injoignable."]);
    } else {
        http_response_code($response['status']);
        echo $response['body'];
    }
} else {
    http_response_code(400);
    echo json_encode(["detail" => "Aucune donnée reçue."]);
}
