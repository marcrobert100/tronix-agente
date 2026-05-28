-- ============================================================
-- Sistema de Apostas - Copa do Mundo & Jogos de Futebol/MMA
-- Banco de Dados: MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS apostas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE apostas_db;

-- ============================================================
-- TABELA: admins (Super-Administradores do Sistema)
-- ============================================================
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    ativo TINYINT(1) DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: bares (Multi-tenant)
-- ============================================================
CREATE TABLE IF NOT EXISTS bares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    telefone VARCHAR(20),
    email VARCHAR(150),
    chave_pix VARCHAR(255) COMMENT 'Chave PIX do bar (CPF, CNPJ, email ou aleatória)',
    nome_pix VARCHAR(150) COMMENT 'Nome do titular da chave PIX',
    logo VARCHAR(255),
    ativo TINYINT(1) DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: donos_bar (Donos de Bar - Login no painel bar/)
-- ============================================================
CREATE TABLE IF NOT EXISTS donos_bar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bar_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    ativo TINYINT(1) DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bar_id) REFERENCES bares(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: clientes (Apostadores - vinculados a um bar)
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bar_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    telefone VARCHAR(20),
    saldo DECIMAL(10,2) DEFAULT 0.00,
    ativo TINYINT(1) DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bar_id) REFERENCES bares(id) ON DELETE CASCADE,
    UNIQUE KEY uk_cliente_bar (email, bar_id)
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: esportes
-- ============================================================
CREATE TABLE IF NOT EXISTS esportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    icone VARCHAR(50) DEFAULT 'bi-controller',
    ativo TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: campeonatos
-- ============================================================
CREATE TABLE IF NOT EXISTS campeonatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    esporte_id INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    temporada VARCHAR(20),
    logo VARCHAR(255),
    ativo TINYINT(1) DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (esporte_id) REFERENCES esportes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: jogos (Eventos/Partidas)
-- ============================================================
CREATE TABLE IF NOT EXISTS jogos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campeonato_id INT NOT NULL,
    time_a VARCHAR(100) NOT NULL,
    time_b VARCHAR(100) NOT NULL,
    logo_a VARCHAR(255),
    logo_b VARCHAR(255),
    data_jogo DATETIME NOT NULL,
    data_limite_aposta DATETIME NOT NULL COMMENT 'Deadline para aceitar apostas',
    placar_a INT DEFAULT NULL,
    placar_b INT DEFAULT NULL,
    vencedor CHAR(1) DEFAULT NULL COMMENT 'A=time_a, B=time_b, E=empate',
    status ENUM('aberto','encerrado_apostas','em_andamento','finalizado','cancelado') DEFAULT 'aberto',
    local VARCHAR(200),
    observacoes TEXT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (campeonato_id) REFERENCES campeonatos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: opcoes_aposta (Odds para cada jogo)
-- ============================================================
CREATE TABLE IF NOT EXISTS opcoes_aposta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jogo_id INT NOT NULL,
    descricao VARCHAR(100) NOT NULL COMMENT 'Ex: Time A vence, Empate, Time B vence, Over 2.5, etc',
    odd DECIMAL(6,2) NOT NULL DEFAULT 1.00,
    resultado VARCHAR(50) DEFAULT NULL COMMENT 'Valor que identifica o resultado (A, B, E, over25, etc)',
    ativo TINYINT(1) DEFAULT 1,
    FOREIGN KEY (jogo_id) REFERENCES jogos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: apostas (Apostas realizadas pelos clientes)
-- ============================================================
CREATE TABLE IF NOT EXISTS apostas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    jogo_id INT NOT NULL,
    opcao_id INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    odd DECIMAL(6,2) NOT NULL COMMENT 'Odd no momento da aposta',
    potencial_retorno DECIMAL(10,2) NOT NULL COMMENT 'valor × odd',
    status ENUM('pendente','ganhou','perdeu','cancelada') DEFAULT 'pendente',
    ganho DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Valor ganho (se ganhou)',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (jogo_id) REFERENCES jogos(id) ON DELETE CASCADE,
    FOREIGN KEY (opcao_id) REFERENCES opcoes_aposta(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: transacoes_pix (Controle de Pagamentos PIX)
-- ============================================================
CREATE TABLE IF NOT EXISTS transacoes_pix (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    bar_id INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    identificador VARCHAR(50) NOT NULL COMMENT 'Código único para identificar o pagamento',
    status ENUM('pendente','confirmado','cancelado','expirado') DEFAULT 'pendente',
    confirmado_por INT DEFAULT NULL COMMENT 'ID do dono do bar que confirmou',
    observacoes TEXT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    confirmado_em DATETIME DEFAULT NULL,
    expira_em DATETIME NOT NULL COMMENT 'Data de expiração da solicitação',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (bar_id) REFERENCES bares(id) ON DELETE CASCADE,
    UNIQUE KEY uk_identificador (identificador)
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: creditos_historico (Movimentação de Créditos)
-- ============================================================
CREATE TABLE IF NOT EXISTS creditos_historico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    tipo ENUM('deposito','aposta','ganho','estorno','debito_manual','credito_manual') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    saldo_anterior DECIMAL(10,2) NOT NULL,
    saldo_posterior DECIMAL(10,2) NOT NULL,
    descricao VARCHAR(255),
    referencia_id INT DEFAULT NULL COMMENT 'ID da aposta ou transação PIX',
    referencia_tipo VARCHAR(50) DEFAULT NULL COMMENT 'aposta, pix, manual',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- TABELA: configuracoes (Configurações por bar)
-- ============================================================
CREATE TABLE IF NOT EXISTS configuracoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bar_id INT NOT NULL UNIQUE,
    aposta_minima DECIMAL(10,2) DEFAULT 5.00,
    aposta_maxima DECIMAL(10,2) DEFAULT 1000.00,
    tempo_expiracao_pix INT DEFAULT 30 COMMENT 'Minutos para expiração do PIX',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bar_id) REFERENCES bares(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- DADOS INICIAIS
-- ============================================================

-- Admin padrão (senha: admin123)
INSERT INTO admins (nome, email, senha) VALUES
('Administrador', 'admin@apostas.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi');

-- Esportes
INSERT INTO esportes (nome, icone) VALUES
('Futebol', 'bi-trophy'),
('MMA', 'bi-lightning'),
('Copa do Mundo', 'bi-globe');

-- Campeonatos de exemplo
INSERT INTO campeonatos (esporte_id, nome, temporada) VALUES
(1, 'Brasileirão Série A', '2026'),
(1, 'Copa do Brasil', '2026'),
(2, 'UFC', '2026'),
(3, 'Copa do Mundo FIFA', '2026'),
(1, 'Champions League', '2025/2026');

-- ============================================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================================
CREATE INDEX idx_jogos_status ON jogos(status);
CREATE INDEX idx_jogos_data_limite ON jogos(data_limite_aposta);
CREATE INDEX idx_apostas_cliente ON apostas(cliente_id);
CREATE INDEX idx_apostas_jogo ON apostas(jogo_id);
CREATE INDEX idx_apostas_status ON apostas(status);
CREATE INDEX idx_transacoes_status ON transacoes_pix(status);
CREATE INDEX idx_transacoes_bar ON transacoes_pix(bar_id);
CREATE INDEX idx_creditos_cliente ON creditos_historico(cliente_id);
