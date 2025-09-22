@echo off
echo Installing enhanced RAG dependencies...
echo.

REM Install PyMuPDF for better PDF processing
echo Installing PyMuPDF...
pip install PyMuPDF==1.23.16

REM Install NLTK for sentence tokenization
echo Installing NLTK...
pip install nltk==3.8.1

REM Download NLTK data
echo Setting up NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); print('NLTK punkt downloaded')"

echo.
echo ✅ Enhanced dependencies installed successfully!
echo.
echo Next steps:
echo 1. Run enhanced ingestion: python enhanced_ingest.py
echo 2. Restart your API: python rag_api.py
echo 3. Test improved accuracy (expected: 58.3%% → 75%%+)
echo.
pause