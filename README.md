# 🎤 VVN AI Analyzer

Uma solução completa para transcrever e analisar gravações de chamadas de vendas do sistema Vivo Voz Negócio (VVN) usando Inteligência Artificial.

## ✨ Funcionalidades

- 🎵 **Transcrição de áudios em massa** com AssemblyAI
- 🧠 **Análise de insights de vendas** com OpenAI GPT-4o-mini
- 👤 **Identificação automática de vendedores** no início das chamadas
- 📊 **Agrupamento de insights** e pontos de melhoria por vendedor
- 🏷️ **Classificação e pontuação** de ligações (A, B, C, D)
- 📄 **Geração de relatórios detalhados em Word** por vendedor
- 🌐 **Interface web** para upload de áudios e download de relatórios
- ☁️ **Deploy fácil** no Glitch

## 🚀 Como Usar

### 1. Deploy no Glitch

1. **Importe o projeto no Glitch:**
   - Vá para [glitch.com](https://glitch.com)
   - Clique em "New Project" → "Import from GitHub"
   - Cole a URL do seu repositório GitHub

2. **Configure as dependências:**
   - O Glitch instalará automaticamente as dependências do `requirements.txt`

3. **Acesse a aplicação:**
   - Sua aplicação estará disponível em `https://seu-projeto.glitch.me`

### 2. Uso Local (Desenvolvimento)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/vvn-ai-analyzer.git
cd vvn-ai-analyzer

# Instale as dependências
cd backend
pip install -r requirements.txt

# Execute a aplicação
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

### 3. Como Usar a Interface

1. **Configure as APIs:**
   - Insira sua chave da AssemblyAI
   - Insira sua chave da OpenAI

2. **Faça upload dos áudios:**
   - Arraste e solte os arquivos de áudio
   - Ou clique para selecionar arquivos
   - Formatos suportados: WAV, MP3, M4A, FLAC, OGG, AAC

3. **Processe os arquivos:**
   - Clique em "Processar Arquivos"
   - Aguarde o processamento (pode levar alguns minutos)

4. **Baixe o relatório:**
   - Após o processamento, clique no link de download
   - Receba um relatório completo em Word

## 📋 Pré-requisitos

### APIs Necessárias

1. **AssemblyAI API:**
   - Crie uma conta em [assemblyai.com](https://www.assemblyai.com/)
   - Obtenha sua chave de API no dashboard
   - Custo aproximado: $0.37 por hora de áudio

2. **OpenAI API:**
   - Crie uma conta em [platform.openai.com](https://platform.openai.com/)
   - Obtenha sua chave de API
   - Custo aproximado: $0.15 por 1M tokens (muito baixo para análises)

## 🏗️ Estrutura do Projeto

```
vvn_ia_analyzer/
├── backend/                    # Backend Flask
│   ├── app.py                 # Aplicação principal
│   ├── transcription_service.py   # Serviço de transcrição
│   ├── analysis_service.py    # Serviço de análise
│   ├── vendor_grouping_service.py # Agrupamento por vendedor
│   ├── classification_service.py  # Classificação de ligações
│   ├── report_generator.py    # Geração de relatórios
│   └── requirements.txt       # Dependências Python
├── glitch.json               # Configuração do Glitch
├── package.json              # Configuração do projeto
├── requirements.txt          # Dependências principais
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Este arquivo
```

## 📊 O que o Relatório Contém

### Por Vendedor:
- 📈 **Nota geral** (1-10)
- 💰 **Taxa de conversão**
- 😊 **Taxa de sentimento positivo**
- ✅ **Pontos fortes principais**
- 🔧 **Áreas de melhoria**
- 🎓 **Prioridades de treinamento**
- 🚀 **Próximos passos**

### Por Ligação:
- 🏷️ **Classificação** (A, B, C, D)
- 📝 **Resumo executivo**
- ❓ **Objeções do cliente**
- 🛍️ **Produtos mencionados**
- 💡 **Recomendações específicas**

### Estatísticas da Equipe:
- 🏆 **Ranking de vendedores**
- 📊 **Métricas consolidadas**
- 💡 **Recomendações gerais**

## 🔧 Tecnologias Utilizadas

- **Backend**: Python 3.8+, Flask
- **Transcrição**: AssemblyAI API
- **Análise de IA**: OpenAI API (GPT-4o-mini)
- **Geração de Documentos**: python-docx
- **Interface Web**: HTML5, CSS3, JavaScript
- **Deploy**: Glitch, Heroku, ou qualquer plataforma Python

## 🛡️ Segurança

- ✅ As chaves de API são inseridas pelo usuário e não armazenadas
- ✅ Arquivos de áudio são processados temporariamente e removidos
- ✅ Relatórios são gerados sob demanda
- ✅ CORS configurado para acesso seguro

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Se você encontrar problemas ou tiver dúvidas:

1. Verifique se as chaves de API estão corretas
2. Confirme que os arquivos de áudio estão em formato suportado
3. Verifique a conexão com a internet
4. Abra uma issue no GitHub para reportar bugs

## 🎯 Roadmap

- [ ] Suporte a mais idiomas
- [ ] Análise de sentimentos mais avançada
- [ ] Dashboard com métricas em tempo real
- [ ] Integração com CRMs
- [ ] API REST para integração externa
- [ ] Análise de tendências temporais

---

**Desenvolvido com ❤️ pela equipe Manus AI**


