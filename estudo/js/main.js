// Sistema de Estudo - JavaScript Principal

document.addEventListener('DOMContentLoaded', function() {
    // ==================== FLASHCARDS ====================
    let currentCard = 0;
    const flashcardContainer = document.getElementById('flashcards');
    const cardCounter = document.getElementById('cardCounter');
    const prevBtn = document.getElementById('prevCard');
    const nextBtn = document.getElementById('nextCard');

    function createFlashcard() {
        const card = document.createElement('div');
        card.className = 'flashcard';
        card.innerHTML = `
            <div class="flashcard-front">
                <h3>${vocabularyData[currentCard].word}</h3>
                <p style="font-size: 0.8rem; margin-top: 10px;">(Clique para ver a tradução)</p>
            </div>
            <div class="flashcard-back">
                <p>${vocabularyData[currentCard].meaning}</p>
            </div>
        `;
        
        card.addEventListener('click', function() {
            this.classList.toggle('flipped');
        });
        
        return card;
    }

    function updateFlashcard() {
        flashcardContainer.innerHTML = '';
        flashcardContainer.appendChild(createFlashcard());
        cardCounter.textContent = `${currentCard + 1} / ${vocabularyData.length}`;
    }

    prevBtn.addEventListener('click', function() {
        currentCard = (currentCard - 1 + vocabularyData.length) % vocabularyData.length;
        updateFlashcard();
    });

    nextBtn.addEventListener('click', function() {
        currentCard = (currentCard + 1) % vocabularyData.length;
        updateFlashcard();
    });

    // Inicializar flashcards
    updateFlashcard();

    // ==================== SIMULADOR DE TRADING ====================
    const calculateBtn = document.getElementById('calculateBtn');
    const resultDiv = document.getElementById('result');

    calculateBtn.addEventListener('click', function() {
        const stockPrice = parseFloat(document.getElementById('stockPrice').value);
        const strikePrice = parseFloat(document.getElementById('strikePrice').value);
        const premium = parseFloat(document.getElementById('premium').value);
        const optionType = document.getElementById('optionType').value;

        let result, profitLoss, status;

        if (optionType === 'call') {
            // Call Option: Lucro se preço > strike + premium
            if (stockPrice > strikePrice) {
                profitLoss = (stockPrice - strikePrice) - premium;
            } else {
                profitLoss = -premium;
            }
        } else {
            // Put Option: Lucro se preço < strike - premium
            if (stockPrice < strikePrice) {
                profitLoss = (strikePrice - stockPrice) - premium;
            } else {
                profitLoss = -premium;
            }
        }

        // Formatar resultado
        const profitLossFormatted = profitLoss.toFixed(2);
        const isProfit = profitLoss > 0;
        
        resultDiv.innerHTML = `
            <div style="color: ${isProfit ? '#27ae60' : '#e74c3c'};">
                ${isProfit ? '📈 LUCRO' : '📉 PERDA'}: $${profitLossFormatted}
            </div>
            <div style="font-size: 0.9rem; margin-top: 10px; opacity: 0.8;">
                Preço Ação: $${stockPrice} | Strike: $${strikePrice} | Premium: $${premium}
            </div>
        `;
    });

    // ==================== QUIZ ====================
    let currentQuiz = 0;
    let score = 0;
    const quizQuestion = document.getElementById('quizQuestion');
    const quizOptions = document.getElementById('quizOptions');
    const quizResult = document.getElementById('quizResult');
    const nextQuestionBtn = document.getElementById('nextQuestion');

    function loadQuiz() {
        const quiz = quizData[currentQuiz];
        quizQuestion.textContent = `${currentQuiz + 1}. ${quiz.question}`;
        quizOptions.innerHTML = '';
        quizResult.textContent = '';
        nextQuestionBtn.style.display = 'none';

        quiz.options.forEach((option, index) => {
            const btn = document.createElement('div');
            btn.className = 'quiz-option';
            btn.textContent = option;
            btn.addEventListener('click', () => checkAnswer(index));
            quizOptions.appendChild(btn);
        });
    }

    function checkAnswer(selectedIndex) {
        const quiz = quizData[currentQuiz];
        const options = quizOptions.querySelectorAll('.quiz-option');
        
        options.forEach((option, index) => {
            option.style.pointerEvents = 'none';
            if (index === quiz.correct) {
                option.classList.add('correct');
            } else if (index === selectedIndex && selectedIndex !== quiz.correct) {
                option.classList.add('wrong');
            }
        });

        if (selectedIndex === quiz.correct) {
            score++;
            quizResult.textContent = '✅ Correto!';
            quizResult.style.color = '#27ae60';
        } else {
            quizResult.textContent = '❌ Incorreto!';
            quizResult.style.color = '#e74c3c';
        }

        nextQuestionBtn.style.display = 'inline-block';
    }

    nextQuestionBtn.addEventListener('click', function() {
        currentQuiz++;
        if (currentQuiz >= quizData.length) {
            // Fim do quiz
            quizQuestion.textContent = `Quiz Concluído!`;
            quizOptions.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <h3>Pontuação: ${score} / ${quizData.length}</h3>
                    <p>${Math.round((score / quizData.length) * 100)}% de acerto</p>
                    <button class="btn" onclick="location.reload()" style="margin-top: 20px;">Reiniciar Quiz</button>
                </div>
            `;
            quizResult.textContent = '';
            nextQuestionBtn.style.display = 'none';
        } else {
            loadQuiz();
        }
    });

    // Inicializar quiz
    loadQuiz();

    // ==================== TEMA ESCURO ====================
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    themeToggle.addEventListener('click', function() {
        body.classList.toggle('dark-mode');
        themeToggle.textContent = body.classList.contains('dark-mode') ? '☀️' : '🌙';
    });

    // ==================== EFEITO DE SCROLL NO CABEÇALHO ====================
    window.addEventListener('scroll', function() {
        const header = document.getElementById('header');
        if (window.scrollY > 50) {
            header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
            header.style.background = 'linear-gradient(135deg, #1a252f, #2c3e50)';
        } else {
            header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
            header.style.background = 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))';
        }
    });

    // ==================== NAVEGAÇÃO SUAVE ====================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});