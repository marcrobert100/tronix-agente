<?php
try {
    $db = new PDO("sqlite:C:/xampp/htdocs/agente/tronix.db");
    $res = $db->query("SELECT status, COUNT(*) as qtd FROM tarefas GROUP BY status");
    $found = false;
    while($row = $res->fetch(PDO::FETCH_ASSOC)) {
        echo "Status: " . $row['status'] . " | Qtd: " . $row['qtd'] . PHP_EOL;
        $found = true;
    }
    if(!$found) echo "Banco conectado, mas está vazio." . PHP_EOL;
} catch (Exception $e) {
    echo "Erro: " . $e->getMessage();
}
?>
