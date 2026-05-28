<?php
/**
 * Header HTML - Layout Base
 */
$pageTitle = $pageTitle ?? SISTEMA_NOME;
$bodyClass = $bodyClass ?? '';
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= sanitize($pageTitle) ?> | <?= SISTEMA_NOME ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link href="<?= ASSETS_URL ?>/css/style.css" rel="stylesheet">
</head>
<body class="<?= $bodyClass ?>">

<?php if ($showNav ?? true): ?>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
    <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="<?= BASE_URL ?>/">
            <i class="bi bi-trophy-fill text-warning"></i> <?= SISTEMA_NOME ?>
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="mainNav">
            <ul class="navbar-nav me-auto">
                <?php if (isset($navType)):
                    switch($navType):
                        case 'admin': ?>
                            <li class="nav-item"><a class="nav-link" href="<?= ADMIN_URL ?>/"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= ADMIN_URL ?>/bares.php"><i class="bi bi-shop"></i> Bares</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= ADMIN_URL ?>/usuarios.php"><i class="bi bi-people"></i> Donos de Bar</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= ADMIN_URL ?>/jogos.php"><i class="bi bi-controller"></i> Jogos</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= ADMIN_URL ?>/resultados.php"><i class="bi bi-flag"></i> Resultados</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= ADMIN_URL ?>/relatorios.php"><i class="bi bi-bar-chart"></i> Relatórios</a></li>
                        <?php break;
                        case 'bar': ?>
                            <li class="nav-item"><a class="nav-link" href="<?= BAR_URL ?>/"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= BAR_URL ?>/apostadores.php"><i class="bi bi-people"></i> Apostadores</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= BAR_URL ?>/apostas.php"><i class="bi bi-bet"></i> Apostas</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= BAR_URL ?>/pagamentos.php"><i class="bi bi-cash-stack"></i> Pagamentos</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= BAR_URL ?>/creditos.php"><i class="bi bi-wallet2"></i> Créditos</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= BAR_URL ?>/jogos.php"><i class="bi bi-controller"></i> Jogos</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= BAR_URL ?>/relatorio.php"><i class="bi bi-bar-chart"></i> Relatório</a></li>
                        <?php break;
                        case 'cliente': ?>
                            <li class="nav-item"><a class="nav-link" href="<?= CLIENTE_URL ?>/"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= CLIENTE_URL ?>/jogos.php"><i class="bi bi-controller"></i> Jogos</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= CLIENTE_URL ?>/minhas_apostas.php"><i class="bi bi-bet"></i> Minhas Apostas</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= CLIENTE_URL ?>/resultados.php"><i class="bi bi-flag"></i> Resultados</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= CLIENTE_URL ?>/creditos.php"><i class="bi bi-wallet2"></i> Créditos</a></li>
                            <li class="nav-item"><a class="nav-link" href="<?= CLIENTE_URL ?>/pix.php"><i class="bi bi-qr-code"></i> Recarregar</a></li>
                        <?php break;
                    endswitch;
                endif; ?>
            </ul>
            <ul class="navbar-nav">
                <?php if ($usuarioLogado ?? false): ?>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            <i class="bi bi-person-circle"></i> <?= sanitize($usuarioLogado['nome']) ?>
                            <?php if ($navType === 'cliente'): ?>
                                <span class="badge bg-warning text-dark ms-1"><?= formatarMoeda($usuarioLogado['saldo']) ?></span>
                            <?php endif; ?>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="<?= $logoutUrl ?? '#' ?>"><i class="bi bi-box-arrow-right"></i> Sair</a></li>
                        </ul>
                    </li>
                <?php endif; ?>
            </ul>
        </div>
    </div>
</nav>
<?php endif; ?>

<main class="container-fluid py-4">
    <?php
    $flash = getFlash();
    if ($flash): ?>
        <div class="alert alert-<?= $flash['tipo'] === 'success' ? 'success' : ($flash['tipo'] === 'error' ? 'danger' : $flash['tipo']) ?> alert-dismissible fade show" role="alert">
            <?= $flash['mensagem'] ?>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    <?php endif; ?>
