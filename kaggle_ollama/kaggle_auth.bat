@echo off
chcp 65001 >nul
title TRONIX - Autorizar Kaggle (1 unico passo seu)
echo.
echo ==============================================================
echo  1) O navegador vai abrir na tela de login do Kaggle.
echo     Entre com sua conta (Google ou e-mail + senha).
echo  2) Clique em "Authorize" / "Permitir".
echo  3) A pagina mostra um CODIGO de verificacao.
echo     COPIE esse codigo e cole aqui embaixo, depois Enter.
echo.
echo  Se voce ainda nao tem conta no Kaggle, feche isto e me avise.
echo ==============================================================
echo.
kaggle auth login
echo.
echo === TESTANDO A CONEXAO ===
kaggle kernels list --mine
echo.
pause
