"""
Aplicação Flask Principal - VVN AI Analyzer
"""
import os
import tempfile
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Importa serviços
from transcription_service import AssemblyAITranscriptionService
from analysis_service import VendorAnalysisService
from vendor_grouping_service import VendorGroupingService
from classification_service import CallClassificationService
from report_generator import WordReportGenerator

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Extensões de arquivo permitidas
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'aac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Página inicial
    """
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VVN AI Analyzer</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 2px dashed #007bff;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                background-color: #f8f9fa;
            }
            .upload-area:hover {
                background-color: #e9ecef;
            }
            .btn {
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
            .btn:hover {
                background-color: #0056b3;
            }
            .btn:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            .progress {
                width: 100%;
                height: 20px;
                background-color: #e9ecef;
                border-radius: 10px;
                margin: 20px 0;
                overflow: hidden;
                display: none;
            }
            .progress-bar {
                height: 100%;
                background-color: #007bff;
                width: 0%;
                transition: width 0.3s ease;
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                border-radius: 5px;
                display: none;
            }
            .status.success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status.info {
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .config-section {
                margin: 30px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            .form-group {
                margin: 15px 0;
            }
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            .form-group input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            .file-list {
                margin: 20px 0;
            }
            .file-item {
                padding: 10px;
                margin: 5px 0;
                background-color: #e9ecef;
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .download-link {
                color: #007bff;
                text-decoration: none;
                font-weight: bold;
            }
            .download-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 VVN AI Analyzer</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                Transcreva e analise gravações de vendas com Inteligência Artificial
            </p>
            
            <div class="config-section">
                <h3>🔑 Configuração das APIs</h3>
                <div class="form-group">
                    <label for="assemblyai-key">Chave AssemblyAI:</label>
                    <input type="password" id="assemblyai-key" placeholder="Sua chave da API AssemblyAI">
                </div>
                <div class="form-group">
                    <label for="openai-key">Chave OpenAI:</label>
                    <input type="password" id="openai-key" placeholder="Sua chave da API OpenAI">
                </div>
            </div>
            
            <div class="upload-area" id="upload-area">
                <h3>📁 Selecione os Arquivos de Áudio</h3>
                <p>Arraste e solte os arquivos aqui ou clique para selecionar</p>
                <p style="color: #666; font-size: 14px;">
                    Formatos suportados: WAV, MP3, M4A, FLAC, OGG, AAC
                </p>
                <input type="file" id="file-input" multiple accept=".wav,.mp3,.m4a,.flac,.ogg,.aac" style="display: none;">
                <button class="btn" onclick="document.getElementById('file-input').click()">
                    Selecionar Arquivos
                </button>
            </div>
            
            <div class="file-list" id="file-list"></div>
            
            <div style="text-align: center;">
                <button class="btn" id="process-btn" onclick="processFiles()" disabled>
                    🚀 Processar Arquivos
                </button>
            </div>
            
            <div class="progress" id="progress">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
            
            <div class="status" id="status"></div>
            
            <div id="download-section" style="display: none; text-align: center; margin-top: 30px;">
                <h3>📄 Relatório Pronto!</h3>
                <a href="#" id="download-link" class="download-link">
                    📥 Baixar Relatório em Word
                </a>
            </div>
        </div>
        
        <script>
            let selectedFiles = [];
            
            // Configuração de drag and drop
            const uploadArea = document.getElementById('upload-area');
            const fileInput = document.getElementById('file-input');
            const fileList = document.getElementById('file-list');
            const processBtn = document.getElementById('process-btn');
            const status = document.getElementById('status');
            const progress = document.getElementById('progress');
            const progressBar = document.getElementById('progress-bar');
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.backgroundColor = '#e9ecef';
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.backgroundColor = '#f8f9fa';
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.backgroundColor = '#f8f9fa';
                handleFiles(e.dataTransfer.files);
            });
            
            fileInput.addEventListener('change', (e) => {
                handleFiles(e.target.files);
            });
            
            function handleFiles(files) {
                selectedFiles = Array.from(files);
                displayFileList();
                updateProcessButton();
            }
            
            function displayFileList() {
                fileList.innerHTML = '';
                selectedFiles.forEach((file, index) => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <span>📄 ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                        <button onclick="removeFile(${index})" style="background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                            ❌ Remover
                        </button>
                    `;
                    fileList.appendChild(fileItem);
                });
            }
            
            function removeFile(index) {
                selectedFiles.splice(index, 1);
                displayFileList();
                updateProcessButton();
            }
            
            function updateProcessButton() {
                const assemblyaiKey = document.getElementById('assemblyai-key').value;
                const openaiKey = document.getElementById('openai-key').value;
                
                processBtn.disabled = !(selectedFiles.length > 0 && assemblyaiKey && openaiKey);
            }
            
            // Atualiza botão quando as chaves são inseridas
            document.getElementById('assemblyai-key').addEventListener('input', updateProcessButton);
            document.getElementById('openai-key').addEventListener('input', updateProcessButton);
            
            function showStatus(message, type) {
                status.className = `status ${type}`;
                status.textContent = message;
                status.style.display = 'block';
            }
            
            function updateProgress(percent) {
                progress.style.display = 'block';
                progressBar.style.width = percent + '%';
            }
            
            async function processFiles() {
                if (selectedFiles.length === 0) {
                    showStatus('Selecione pelo menos um arquivo de áudio', 'error');
                    return;
                }
                
                const assemblyaiKey = document.getElementById('assemblyai-key').value;
                const openaiKey = document.getElementById('openai-key').value;
                
                if (!assemblyaiKey || !openaiKey) {
                    showStatus('Insira as chaves das APIs AssemblyAI e OpenAI', 'error');
                    return;
                }
                
                processBtn.disabled = true;
                showStatus('Iniciando processamento...', 'info');
                updateProgress(0);
                
                try {
                    const formData = new FormData();
                    
                    selectedFiles.forEach((file, index) => {
                        formData.append('audio_files', file);
                    });
                    
                    formData.append('assemblyai_key', assemblyaiKey);
                    formData.append('openai_key', openaiKey);
                    
                    const response = await fetch('/process', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Erro HTTP: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateProgress(100);
                        showStatus('Processamento concluído com sucesso!', 'success');
                        
                        // Mostra link de download
                        const downloadSection = document.getElementById('download-section');
                        const downloadLink = document.getElementById('download-link');
                        downloadLink.href = `/download/${result.report_id}`;
                        downloadSection.style.display = 'block';
                    } else {
                        throw new Error(result.error || 'Erro desconhecido');
                    }
                    
                } catch (error) {
                    showStatus(`Erro: ${error.message}`, 'error');
                    updateProgress(0);
                } finally {
                    processBtn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/process', methods=['POST'])
def process_audio_files():
    """
    Processa arquivos de áudio enviados
    """
    try:
        # Verifica se há arquivos
        if 'audio_files' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})
        
        files = request.files.getlist('audio_files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'})
        
        # Verifica chaves das APIs
        assemblyai_key = request.form.get('assemblyai_key')
        openai_key = request.form.get('openai_key')
        
        if not assemblyai_key or not openai_key:
            return jsonify({'success': False, 'error': 'Chaves das APIs são obrigatórias'})
        
        # Salva arquivos temporariamente
        temp_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
                file.save(temp_path)
                temp_files.append(temp_path)
        
        if not temp_files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo válido encontrado'})
        
        # Inicializa serviços
        transcription_service = AssemblyAITranscriptionService(assemblyai_key)
        analysis_service = VendorAnalysisService(openai_key)
        grouping_service = VendorGroupingService()
        classification_service = CallClassificationService()
        report_generator = WordReportGenerator()
        
        # 1. Transcrição
        print("🎤 Iniciando transcrição...")
        transcriptions = transcription_service.transcribe_multiple_files(temp_files)
        
        if not transcriptions:
            return jsonify({'success': False, 'error': 'Falha na transcrição dos arquivos'})
        
        # 2. Análise
        print("🧠 Iniciando análise...")
        analyzed_conversations = analysis_service.analyze_multiple_conversations(transcriptions)
        
        # 3. Classificação
        print("🏷️ Classificando ligações...")
        classified_conversations = classification_service.classify_multiple_calls(analyzed_conversations)
        
        # 4. Agrupamento por vendedor
        print("👥 Agrupando por vendedor...")
        vendor_data = grouping_service.process_all_vendors(classified_conversations)
        
        # 5. Geração do relatório
        print("📄 Gerando relatório...")
        report_id = str(uuid.uuid4())
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], f"relatorio_vvn_{report_id}.docx")
        
        report_generator.generate_comprehensive_report(vendor_data, report_path)
        
        # Limpa arquivos temporários
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'summary': {
                'total_files': len(temp_files),
                'total_transcriptions': len(transcriptions),
                'total_vendors': vendor_data.get('total_vendedores', 0),
                'total_conversations': vendor_data.get('total_conversas', 0)
            }
        })
        
    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<report_id>')
def download_report(report_id):
    """
    Download do relatório gerado
    """
    try:
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], f"relatorio_vvn_{report_id}.docx")
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Relatório não encontrado'}), 404
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"relatorio_vvn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """
    Verificação de saúde da aplicação
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Cria diretório de upload se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Executa aplicação
    app.run(host='0.0.0.0', port=5000, debug=True)

