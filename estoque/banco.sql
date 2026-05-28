-- ============================================
-- PCsolucoes - Controle de Estoque
-- Script de criacao do banco de dados
-- ============================================

CREATE DATABASE IF NOT EXISTS estoque_pcsolucoes
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE estoque_pcsolucoes;

-- Tabela de categorias
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    categoria_id INT,
    codigo_barras VARCHAR(50),
    preco_custo DECIMAL(10,2) DEFAULT 0.00,
    preco_venda DECIMAL(10,2) DEFAULT 0.00,
    quantidade INT DEFAULT 0,
    estoque_minimo INT DEFAULT 5,
    unidade VARCHAR(20) DEFAULT 'UN',
    ativo TINYINT(1) DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabela de movimentacoes
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    tipo ENUM('entrada', 'saida') NOT NULL,
    quantidade INT NOT NULL,
    motivo VARCHAR(200),
    usuario VARCHAR(100) DEFAULT 'sistema',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Inserir categorias padrao
INSERT INTO categorias (nome) VALUES
('Informática'),
('Periféricos'),
('Redes'),
('Acessórios'),
('Software');

-- Inserir produtos de exemplo
INSERT INTO produtos (nome, descricao, categoria_id, preco_custo, preco_venda, quantidade, estoque_minimo, unidade) VALUES
('Mouse USB', 'Mouse óptico USB com 3 botões', 2, 25.00, 49.90, 50, 10, 'UN'),
('Teclado ABNT2', 'Teclado USB ABNT2 com 104 teclas', 2, 35.00, 69.90, 30, 10, 'UN'),
('Cabo de Rede Cat6', 'Cabo de rede Cat6 1 metro', 3, 8.00, 19.90, 100, 20, 'MT'),
('Monitor 24"', 'Monitor LED 24 polegadas Full HD', 1, 800.00, 1299.00, 15, 5, 'UN'),
('SSD 240GB', 'SSD SATA 240GB', 1, 150.00, 249.90, 25, 8, 'UN'),
('Windows 11 Pro', 'Licença Windows 11 Professional', 5, 200.00, 499.00, 50, 10, 'LIC');
