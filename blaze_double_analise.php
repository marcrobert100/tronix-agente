<?php
class BlazeDoubleSimulator {
    private const WEIGHTS = [
        'W' => 1,   // White (0) - ~13%
        'R' => 7,   // Red (1-7) - ~44%
        'B' => 7    // Black (8-14) - ~43%
    ];
    
    private const TOTAL_WEIGHT = 15;
    
    private array $history = [];
    private int $rounds;
    
    public function __construct(int $rounds = 1000) {
        $this->rounds = $rounds;
    }
    
    public function generateResult(): string {
        $rand = random_int(1, self::TOTAL_WEIGHT);
        
        if ($rand <= self::WEIGHTS['W']) {
            return 'W';
        } elseif ($rand <= self::WEIGHTS['W'] + self::WEIGHTS['R']) {
            return 'R';
        }
        return 'B';
    }
    
    public function simulate(int $rounds = null): array {
        $rounds = $rounds ?? $this->rounds;
        $results = [];
        
        for ($i = 0; $i < $rounds; $i++) {
            $results[] = $this->generateResult();
        }
        
        $this->history = $results;
        return $results;
    }
    
    public function getFrequencies(): array {
        $count = array_count_values($this->history);
        $total = count($this->history);
        
        return [
            'W' => [
                'count' => $count['W'] ?? 0,
                'percentage' => round(($count['W'] ?? 0) / $total * 100, 2)
            ],
            'R' => [
                'count' => $count['R'] ?? 0,
                'percentage' => round(($count['R'] ?? 0) / $total * 100, 2)
            ],
            'B' => [
                'count' => $count['B'] ?? 0,
                'percentage' => round(($count['B'] ?? 0) / $total * 100, 2)
            ]
        ];
    }
    
    public function getStreaks(): array {
        $streaks = ['W' => [], 'R' => [], 'B' => []];
        $current = null;
        $count = 0;
        
        foreach ($this->history as $color) {
            if ($color === $current) {
                $count++;
            } else {
                if ($current !== null) {
                    $streaks[$current][] = $count;
                }
                $current = $color;
                $count = 1;
            }
        }
        
        if ($current !== null) {
            $streaks[$current][] = $count;
        }
        
        $result = [];
        foreach ($streaks as $color => $values) {
            $result[$color] = [
                'max' => !empty($values) ? max($values) : 0,
                'avg' => !empty($values) ? round(array_sum($values) / count($values), 2) : 0
            ];
        }
        
        return $result;
    }
    
    public function getChiSquare(array $expected): float {
        $observed = array_count_values($this->history);
        $total = count($this->history);
        $chiSquare = 0;
        
        foreach ($expected as $color => $prob) {
            $exp = $total * $prob;
            $obs = $observed[$color] ?? 0;
            $chiSquare += pow($obs - $exp, 2) / $exp;
        }
        
        return round($chiSquare, 4);
    }
    
    public function runAnalysis(): void {
        echo "==========================================\n";
        echo "    BLAZE DOUBLE - ANALISE ESTATISTICA\n";
        echo "==========================================\n\n";
        
        echo "TABELA DE FREQUENCIAS (1.000 rodadas)\n";
        echo "----------------------------------------\n";
        printf("| Cor   | Quantidade | Percentual | Esperado |\n");
        printf("|--------|------------|-------------|----------|\n");
        
        $freq = $this->getFrequencies();
        $expected = ['W' => 0.133, 'R' => 0.440, 'B' => 0.427];
        
        foreach ($freq as $color => $data) {
            $name = $color === 'W' ? 'White' : ($color === 'R' ? 'Red' : 'Black');
            $expPct = round($expected[$color] * 100, 1);
            printf("| %-5s |    %3d     |   %6.2f%%    |  %5.1f%%  |\n", 
                $name, $data['count'], $data['percentage'], $expPct);
        }
        
        echo "----------------------------------------\n\n";
        
        echo "ANALISE DE SEQUENCIAS\n";
        echo "----------------------------------------\n";
        $streaks = $this->getStreaks();
        foreach ($streaks as $color => $data) {
            $name = $color === 'W' ? 'White' : ($color === 'R' ? 'Red' : 'Black');
            echo "{$name}: Max={$data['max']}, Media={$data['avg']}\n";
        }
        
        echo "\nTESTE QUI-QUADRADO\n";
        echo "----------------------------------------\n";
        $chiSquare = $this->getChiSquare($expected);
        echo "Valor chi2: {$chiSquare}\n";
        echo "Valor critico (p=0.05, gl=2): 5.991\n";
        
        if ($chiSquare < 5.991) {
            echo "Distribuicao uniforme confirmada\n";
        } else {
            echo "Desvio significativo detectado\n";
        }
        
        echo "\n==========================================\n";
    }
}

$simulator = new BlazeDoubleSimulator(1000);
$simulator->simulate();
$simulator->runAnalysis();
