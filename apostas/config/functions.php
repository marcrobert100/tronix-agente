<?php
/**
 * Funções Utilitárias do Sistema
 */

require_once __DIR__ . '/database.php';
require_once __DIR__ . '/config.php';

// ============================================================
// AUTENTICAÇÃO
// ============================================================

function hashSenha(string $senha): string {
    return password_hash($senha, PASSWORD_DEFAULT);
}

function verificarSenha(string $senha, string $hash): bool {
    return password_verify($senha, $hash);
}

function isLoggedIn(string $tipo): bool {
    return isset($_SESSION["{$tipo}_id"]);
}

function getUsuarioLogado(string $tipo): ?array {
    if (!isLoggedIn($tipo)) return null;
    $id = $_SESSION["{$tipo}_id"];

    $tabelas = [
        'admin' => 'admins',
        'bar'   => 'donos_bar',
        'cliente' => 'clientes'
    ];

    if (!isset($tabelas[$tipo])) return null;

    $pdo = getConnection();
    $stmt = $pdo->prepare("SELECT * FROM {$tabelas[$tipo]} WHERE id = ? AND ativo = 1");
    $stmt->execute([$id]);
    return $stmt->fetch() ?: null;
}

function requireLogin(string $tipo): void {
    if (!isLoggedIn($tipo)) {
        $urls = ['admin' => ADMIN_URL, 'bar' => BAR_URL, 'cliente' => CLIENTE_URL];
        header("Location: {$urls[$tipo]}/login.php");
        exit;
    }
}

// ============================================================
// PIX
// ============================================================

function gerarIdentificadorPIX(): string {
    return strtoupper(substr(md5(uniqid(mt_rand(), true)), 0, 8) . '-' . date('YmdHis'));
}

function solicitarPIX(int $clienteId, int $barId, float $valor): array {
    $pdo = getConnection();
    $identificador = gerarIdentificadorPIX();
    $expiraEm = date('Y-m-d H:i:s', strtotime('+' . PIX_TEMPO_EXPIRACAO . ' minutes'));

    $stmt = $pdo->prepare("
        INSERT INTO transacoes_pix (cliente_id, bar_id, valor, identificador, expira_em)
        VALUES (?, ?, ?, ?, ?)
    ");
    $stmt->execute([$clienteId, $barId, $valor, $identificador, $expiraEm]);

    return [
        'id' => $pdo->lastInsertId(),
        'identificador' => $identificador,
        'valor' => $valor,
        'chave_pix' => PIX_CHAVE,
        'nome_pix' => PIX_NOME,
        'expira_em' => $expiraEm
    ];
}

function confirmarPIX(int $transacaoId, int $donoBarId): bool {
    $pdo = getConnection();
    $pdo->beginTransaction();

    try {
        // Buscar transação
        $stmt = $pdo->prepare("SELECT * FROM transacoes_pix WHERE id = ? AND status = 'pendente' FOR UPDATE");
        $stmt->execute([$transacaoId]);
        $transacao = $stmt->fetch();

        if (!$transacao) {
            $pdo->rollBack();
            return false;
        }

        // Verificar se não expirou
        if (strtotime($transacao['expira_em']) < time()) {
            $pdo->prepare("UPDATE transacoes_pix SET status = 'expirado' WHERE id = ?")->execute([$transacaoId]);
            $pdo->rollBack();
            return false;
        }

        // Confirmar transação
        $stmt = $pdo->prepare("UPDATE transacoes_pix SET status = 'confirmado', confirmado_por = ?, confirmado_em = NOW() WHERE id = ?");
        $stmt->execute([$donoBarId, $transacaoId]);

        // Creditar saldo do cliente
        $stmt = $pdo->prepare("SELECT saldo FROM clientes WHERE id = ? FOR UPDATE");
        $stmt->execute([$transacao['cliente_id']]);
        $cliente = $stmt->fetch();
        $saldoAnterior = $cliente['saldo'];
        $saldoPosterior = $saldoAnterior + $transacao['valor'];

        $stmt = $pdo->prepare("UPDATE clientes SET saldo = ? WHERE id = ?");
        $stmt->execute([$saldoPosterior, $transacao['cliente_id']]);

        // Registrar no histórico
        registrarCredito(
            $pdo,
            $transacao['cliente_id'],
            'deposito',
            $transacao['valor'],
            $saldoAnterior,
            $saldoPosterior,
            "PIX confirmado - Identificador: {$transacao['identificador']}",
            $transacaoId,
            'pix'
        );

        $pdo->commit();
        return true;
    } catch (Exception $e) {
        $pdo->rollBack();
        error_log("Erro ao confirmar PIX: " . $e->getMessage());
        return false;
    }
}

// ============================================================
// CRÉDITOS
// ============================================================

function registrarCredito(PDO $pdo, int $clienteId, string $tipo, float $valor, float $saldoAnterior, float $saldoPosterior, string $descricao, ?int $referenciaId = null, ?string $referenciaTipo = null): void {
    $stmt = $pdo->prepare("
        INSERT INTO creditos_historico (cliente_id, tipo, valor, saldo_anterior, saldo_posterior, descricao, referencia_id, referencia_tipo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ");
    $stmt->execute([$clienteId, $tipo, $valor, $saldoAnterior, $saldoPosterior, $descricao, $referenciaId, $referenciaTipo]);
}

function creditarManual(PDO $pdo, int $clienteId, float $valor, string $descricao, int $adminId): bool {
    $pdo->beginTransaction();
    try {
        $stmt = $pdo->prepare("SELECT saldo FROM clientes WHERE id = ? FOR UPDATE");
        $stmt->execute([$clienteId]);
        $cliente = $stmt->fetch();
        if (!$cliente) { $pdo->rollBack(); return false; }

        $saldoAnterior = $cliente['saldo'];
        $saldoPosterior = $saldoAnterior + $valor;

        $stmt = $pdo->prepare("UPDATE clientes SET saldo = ? WHERE id = ?");
        $stmt->execute([$saldoPosterior, $clienteId]);

        registrarCredito($pdo, $clienteId, 'credito_manual', $valor, $saldoAnterior, $saldoPosterior, $descricao, null, 'manual');

        $pdo->commit();
        return true;
    } catch (Exception $e) {
        $pdo->rollBack();
        return false;
    }
}

function debitarManual(PDO $pdo, int $clienteId, float $valor, string $descricao, int $adminId): bool {
    $pdo->beginTransaction();
    try {
        $stmt = $pdo->prepare("SELECT saldo FROM clientes WHERE id = ? FOR UPDATE");
        $stmt->execute([$clienteId]);
        $cliente = $stmt->fetch();
        if (!$cliente || $cliente['saldo'] < $valor) { $pdo->rollBack(); return false; }

        $saldoAnterior = $cliente['saldo'];
        $saldoPosterior = $saldoAnterior - $valor;

        $stmt = $pdo->prepare("UPDATE clientes SET saldo = ? WHERE id = ?");
        $stmt->execute([$saldoPosterior, $clienteId]);

        registrarCredito($pdo, $clienteId, 'debito_manual', $valor, $saldoAnterior, $saldoPosterior, $descricao, null, 'manual');

        $pdo->commit();
        return true;
    } catch (Exception $e) {
        $pdo->rollBack();
        return false;
    }
}

// ============================================================
// APOSTAS
// ============================================================

function fazerAposta(int $clienteId, int $jogoId, int $opcaoId, float $valor): array {
    $pdo = getConnection();
    $pdo->beginTransaction();

    try {
        // Verificar cliente e saldo
        $stmt = $pdo->prepare("SELECT * FROM clientes WHERE id = ? AND ativo = 1 FOR UPDATE");
        $stmt->execute([$clienteId]);
        $cliente = $stmt->fetch();
        if (!$cliente) { $pdo->rollBack(); return ['erro' => 'Cliente não encontrado']; }
        if ($cliente['saldo'] < $valor) { $pdo->rollBack(); return ['erro' => 'Saldo insuficiente']; }

        // Buscar configuração do bar
        $stmt = $pdo->prepare("SELECT * FROM configuracoes WHERE bar_id = ?");
        $stmt->execute([$cliente['bar_id']]);
        $config = $stmt->fetch();
        $apostaMin = $config['aposta_minima'] ?? APOSTA_MINIMA;
        $apostaMax = $config['aposta_maxima'] ?? APOSTA_MAXIMA;

        if ($valor < $apostaMin) { $pdo->rollBack(); return ['erro' => "Aposta mínima: R$ " . number_format($apostaMin, 2, ',', '.')]; }
        if ($valor > $apostaMax) { $pdo->rollBack(); return ['erro' => "Aposta máxima: R$ " . number_format($apostaMax, 2, ',', '.')]; }

        // Verificar jogo
        $stmt = $pdo->prepare("SELECT * FROM jogos WHERE id = ? AND status = 'aberto'");
        $stmt->execute([$jogoId]);
        $jogo = $stmt->fetch();
        if (!$jogo) { $pdo->rollBack(); return ['erro' => 'Jogo não disponível para apostas']; }

        // Verificar prazo
        if (strtotime($jogo['data_limite_aposta']) < time()) {
            $pdo->prepare("UPDATE jogos SET status = 'encerrado_apostas' WHERE id = ? AND status = 'aberto'")->execute([$jogoId]);
            $pdo->rollBack();
            return ['erro' => 'O prazo para apostas neste jogo já encerrou'];
        }

        // Verificar opção de aposta
        $stmt = $pdo->prepare("SELECT * FROM opcoes_aposta WHERE id = ? AND jogo_id = ? AND ativo = 1");
        $stmt->execute([$opcaoId, $jogoId]);
        $opcao = $stmt->fetch();
        if (!$opcao) { $pdo->rollBack(); return ['erro' => 'Opção de aposta inválida']; }

        // Calcular potencial retorno
        $potencialRetorno = round($valor * $opcao['odd'], 2);

        // Debitar saldo
        $saldoAnterior = $cliente['saldo'];
        $saldoPosterior = $saldoAnterior - $valor;
        $stmt = $pdo->prepare("UPDATE clientes SET saldo = ? WHERE id = ?");
        $stmt->execute([$saldoPosterior, $clienteId]);

        // Registrar aposta
        $stmt = $pdo->prepare("
            INSERT INTO apostas (cliente_id, jogo_id, opcao_id, valor, odd, potencial_retorno)
            VALUES (?, ?, ?, ?, ?, ?)
        ");
        $stmt->execute([$clienteId, $jogoId, $opcaoId, $valor, $opcao['odd'], $potencialRetorno]);
        $apostaId = $pdo->lastInsertId();

        // Registrar débito no histórico
        registrarCredito(
            $pdo, $clienteId, 'aposta', $valor, $saldoAnterior, $saldoPosterior,
            "Aposta #{$apostaId} - {$jogo['time_a']} vs {$jogo['time_b']} ({$opcao['descricao']})",
            $apostaId, 'aposta'
        );

        $pdo->commit();
        return ['sucesso' => true, 'aposta_id' => $apostaId, 'potencial_retorno' => $potencialRetorno];
    } catch (Exception $e) {
        $pdo->rollBack();
        error_log("Erro ao fazer aposta: " . $e->getMessage());
        return ['erro' => 'Erro ao processar aposta. Tente novamente.'];
    }
}

// ============================================================
// RESULTADOS (Processamento Automático)
// ============================================================

function processarResultado(int $jogoId): bool {
    $pdo = getConnection();
    $pdo->beginTransaction();

    try {
        $stmt = $pdo->prepare("SELECT * FROM jogos WHERE id = ? AND status IN ('aberto','encerrado_apostas','em_andamento')");
        $stmt->execute([$jogoId]);
        $jogo = $stmt->fetch();
        if (!$jogo || $jogo['vencedor'] === null) { $pdo->rollBack(); return false; }

        // Atualizar status para finalizado
        $pdo->prepare("UPDATE jogos SET status = 'finalizado' WHERE id = ?")->execute([$jogoId]);

        // Buscar todas as apostas pendentes
        $stmt = $pdo->prepare("
            SELECT a.*, oa.resultado, c.bar_id
            FROM apostas a
            JOIN opcoes_aposta oa ON a.opcao_id = oa.id
            JOIN clientes c ON a.cliente_id = c.id
            WHERE a.jogo_id = ? AND a.status = 'pendente'
        ");
        $stmt->execute([$jogoId]);
        $apostas = $stmt->fetchAll();

        foreach ($apostas as $aposta) {
            if ($aposta['resultado'] === $jogo['vencedor']) {
                // GANHOU
                $ganho = $aposta['potencial_retorno'];
                $pdo->prepare("UPDATE apostas SET status = 'ganhou', ganho = ? WHERE id = ?")->execute([$ganho, $aposta['id']]);

                // Creditar prêmio
                $stmt2 = $pdo->prepare("SELECT saldo FROM clientes WHERE id = ? FOR UPDATE");
                $stmt2->execute([$aposta['cliente_id']]);
                $saldoAnterior = $stmt2->fetch()['saldo'];
                $saldoPosterior = $saldoAnterior + $ganho;

                $pdo->prepare("UPDATE clientes SET saldo = ? WHERE id = ?")->execute([$saldoPosterior, $aposta['cliente_id']]);

                registrarCredito(
                    $pdo, $aposta['cliente_id'], 'ganho', $ganho, $saldoAnterior, $saldoPosterior,
                    "Aposta #{$aposta['id']} - GANHOU! ({$jogo['time_a']} vs {$jogo['time_b']})",
                    $aposta['id'], 'aposta'
                );
            } else {
                // PERDEU
                $pdo->prepare("UPDATE apostas SET status = 'perdeu' WHERE id = ?")->execute([$aposta['id']]);
            }
        }

        $pdo->commit();
        return true;
    } catch (Exception $e) {
        $pdo->rollBack();
        error_log("Erro ao processar resultado: " . $e->getMessage());
        return false;
    }
}

// ============================================================
// FORMATAÇÃO
// ============================================================

function formatarMoeda(float $valor): string {
    return 'R$ ' . number_format($valor, 2, ',', '.');
}

function formatarData(string $data, string $formato = 'd/m/Y H:i'): string {
    return date($formato, strtotime($data));
}

function formatarCPF(string $cpf): string {
    return preg_replace('/(\d{3})(\d{3})(\d{3})(\d{2})/', '$1.$2.$3-$4', $cpf);
}

function statusLabel(string $status): string {
    $labels = [
        'aberto' => '<span class="badge bg-success">Aberto</span>',
        'encerrado_apostas' => '<span class="badge bg-warning">Encerrado</span>',
        'em_andamento' => '<span class="badge bg-info">Ao Vivo</span>',
        'finalizado' => '<span class="badge bg-secondary">Finalizado</span>',
        'cancelado' => '<span class="badge bg-danger">Cancelado</span>',
        'pendente' => '<span class="badge bg-warning">Pendente</span>',
        'ganhou' => '<span class="badge bg-success">Ganhou</span>',
        'perdeu' => '<span class="badge bg-danger">Perdeu</span>',
        'confirmado' => '<span class="badge bg-success">Confirmado</span>',
        'expirado' => '<span class="badge bg-secondary">Expirado</span>',
    ];
    return $labels[$status] ?? '<span class="badge bg-dark">' . ucfirst($status) . '</span>';
}

function tempoRestante(string $dataLimite): string {
    $diff = strtotime($dataLimite) - time();
    if ($diff <= 0) return 'Encerrado';

    $dias = floor($diff / 86400);
    $horas = floor(($diff % 86400) / 3600);
    $minutos = floor(($diff % 3600) / 60);
    $segundos = $diff % 60;

    if ($dias > 0) return "{$dias}d {$horas}h {$minutos}m";
    if ($horas > 0) return "{$horas}h {$minutos}m {$segundos}s";
    return "{$minutos}m {$segundos}s";
}
