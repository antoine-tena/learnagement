-- Liens d'activation des comptes internes : l'administratif en crée un, la personne choisit
-- son mot de passe en l'ouvrant. Seule l'empreinte SHA-256 du jeton est gardée ; instants en UTC.
CREATE TABLE IF NOT EXISTS `LNM_account_activation` (
    `id_account_activation` INT AUTO_INCREMENT PRIMARY KEY,
    `token_digest` CHAR(64) NOT NULL,
    `login` VARCHAR(100) NOT NULL,
    `id_administratif` INT NOT NULL,
    `expires_at` DATETIME NOT NULL,
    `used_at` DATETIME DEFAULT NULL,

    UNIQUE KEY `SECONDARY` (`token_digest`),
    KEY `idx_account_activation_login` (`login`),

    CONSTRAINT `fk_activation_administratif` FOREIGN KEY (`id_administratif`)
        REFERENCES `LNM_administratif`(`id_administratif`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
