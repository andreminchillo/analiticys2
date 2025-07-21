"""
Serviço de Análise de Insights usando OpenAI
"""
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI


class VendorAnalysisService:
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model_name = model_name
    
    def extract_vendor_name(self, transcription_text: str) -> Optional[str]:
        """
        Extrai o nome do vendedor do início da transcrição
        
        Args:
            transcription_text: Texto da transcrição
            
        Returns:
            Nome do vendedor ou None se não encontrado
        """
        try:
            # Pega os primeiros 500 caracteres da transcrição
            inicio_transcricao = transcription_text[:500]
            
            prompt = f"""
            Analise o início desta transcrição de uma ligação de vendas e identifique o nome do vendedor.
            O vendedor geralmente se apresenta no início da ligação dizendo algo como:
            - "Aqui é o João da Vivo"
            - "Meu nome é Maria, da equipe comercial"
            - "Fala João aqui"
            - "Oi, eu sou a Ana"
            
            INÍCIO DA TRANSCRIÇÃO:
            {inicio_transcricao}
            
            Responda APENAS com o primeiro nome do vendedor (sem sobrenome), ou "NÃO_IDENTIFICADO" se não conseguir identificar.
            Exemplos de resposta: "João", "Maria", "Ana", "NÃO_IDENTIFICADO"
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é especialista em identificar nomes de vendedores em transcrições de ligações. Responda sempre com apenas o primeiro nome ou 'NÃO_IDENTIFICADO'."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            vendor_name = response.choices[0].message.content.strip()
            
            # Limpa e valida o nome
            if vendor_name and vendor_name != "NÃO_IDENTIFICADO":
                # Remove caracteres especiais e mantém apenas letras
                vendor_name = re.sub(r'[^a-zA-ZÀ-ÿ]', '', vendor_name)
                if len(vendor_name) >= 2:  # Nome deve ter pelo menos 2 caracteres
                    return vendor_name.capitalize()
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair nome do vendedor: {str(e)}")
            return None
    
    def analyze_sales_conversation(self, transcription_text: str, vendor_name: str = None, file_name: str = None) -> Dict:
        """
        Analisa uma conversa de vendas e extrai insights detalhados
        
        Args:
            transcription_text: Texto da transcrição
            vendor_name: Nome do vendedor (opcional)
            file_name: Nome do arquivo original (opcional)
            
        Returns:
            Dicionário com análise completa da conversa
        """
        try:
            print(f"🧠 Analisando conversa de vendas...")
            
            prompt = f"""
            Você é um especialista em análise de vendas com 20 anos de experiência. Analise esta transcrição de uma ligação de vendas do sistema VVN (Vivo Voz Negócio) e forneça insights práticos e acionáveis.

            TRANSCRIÇÃO DA LIGAÇÃO:
            {transcription_text}

            INSTRUÇÕES PARA ANÁLISE:
            1. Identifique claramente quem é o VENDEDOR e quem é o CLIENTE na conversa
            2. Analise o comportamento, técnicas e performance do vendedor
            3. Avalie as reações, objeções e interesse do cliente
            4. Foque em insights que podem melhorar as vendas futuras
            5. Seja específico e prático nas suas observações

            Forneça sua análise em formato JSON com estas informações específicas:

            {{
              "sentimento_geral": "positivo/neutro/negativo",
              "score_sentimento": -1.0 a 1.0,
              "satisfacao_cliente": "alta/media/baixa",
              "performance_vendedor": "excelente/boa/regular/ruim",
              "nota_vendedor": 1 a 10,
              
              "produtos_mencionados": ["liste produtos/serviços específicos mencionados"],
              
              "objecoes_cliente": ["liste objeções específicas do cliente como: preço alto, não precisa agora, etc."],
              
              "tecnicas_vendas_usadas": ["identifique técnicas como: rapport, descoberta de necessidades, apresentação de benefícios, fechamento, etc."],
              
              "pontos_fortes": ["o que o vendedor fez bem: escuta ativa, argumentação convincente, etc."],
              
              "pontos_melhoria": ["o que o vendedor pode melhorar: não interrompeu cliente, não perguntou sobre orçamento, etc."],
              
              "resultado_conversa": "venda_fechada/follow_up_agendado/cliente_perdido/indefinido",
              
              "proximos_passos": ["ações específicas recomendadas: ligar em X dias, enviar proposta, agendar visita, etc."],
              
              "palavras_chave": ["termos importantes mencionados pelo cliente"],
              
              "duracao_estimada": "X minutos",
              
              "nivel_interesse_cliente": "alto/medio/baixo",
              
              "resumo_executivo": "Resumo de 2-3 frases explicando o que aconteceu na ligação e o resultado",
              
              "momento_critico": "Identifique o momento mais importante da conversa (quando cliente demonstrou interesse, fez objeção principal, etc.)",
              
              "oportunidades_perdidas": ["o que o vendedor poderia ter feito diferente para melhorar o resultado"],
              
              "cliente_perfil": "Descreva brevemente o perfil do cliente (empresa pequena/média/grande, setor, necessidades)",
              
              "valor_mencionado": "Se algum valor/preço foi mencionado na conversa",
              
              "concorrentes_citados": ["se outros fornecedores foram mencionados"],
              
              "urgencia_compra": "alta/media/baixa - baseado na necessidade demonstrada pelo cliente",
              
              "qualidade_ligacao": "excelente/boa/regular/ruim - considerando clareza da conversa",
              
              "recomendacoes_especificas": ["sugestões práticas para este vendedor melhorar em próximas ligações"],
              
              "classificacao_ligacao": "A/B/C/D - onde A=excelente, B=boa, C=regular, D=ruim"
            }}

            IMPORTANTE: 
            - Seja específico e prático nas suas observações
            - Base suas conclusões apenas no que está na transcrição
            - Se algo não estiver claro na transcrição, indique "não identificado"
            - Foque em insights que ajudem a melhorar vendas futuras
            - A nota do vendedor deve ser de 1 a 10, considerando técnicas, resultado e profissionalismo
            - Responda APENAS com o JSON válido, sem texto adicional
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de vendas. Analise conversas comerciais e forneça insights práticos e acionáveis para melhorar performance de vendas. Sempre responda em JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2500
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Limpa possíveis marcadores de código
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:]
            if analysis_text.endswith("```"):
                analysis_text = analysis_text[:-3]
            
            analysis = json.loads(analysis_text)
            
            # Adiciona metadados
            analysis["vendedor"] = vendor_name or "Não identificado"
            analysis["arquivo_origem"] = file_name or "Não informado"
            analysis["timestamp_analise"] = datetime.now().isoformat()
            analysis["modelo_usado"] = self.model_name
            analysis["tamanho_transcricao"] = len(transcription_text)
            
            print(f"✅ Análise concluída - Sentimento: {analysis.get('sentimento_geral', 'N/A')} | Nota: {analysis.get('nota_vendedor', 'N/A')}")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON da análise: {str(e)}")
            return self._fallback_analysis(transcription_text, vendor_name, file_name)
        except Exception as e:
            print(f"❌ Erro na análise: {str(e)}")
            return self._fallback_analysis(transcription_text, vendor_name, file_name)
    
    def _fallback_analysis(self, transcription_text: str, vendor_name: str = None, file_name: str = None) -> Dict:
        """
        Análise simplificada em caso de falha na análise principal
        """
        try:
            print("🔄 Tentando análise simplificada...")
            
            prompt = f"""
            Analise esta conversa de vendas e responda de forma estruturada:

            CONVERSA: {transcription_text[:2000]}...

            Responda em formato JSON:
            {{
              "sentimento_geral": "positivo/neutro/negativo",
              "performance_vendedor": "excelente/boa/regular/ruim",
              "nota_vendedor": 1 a 10,
              "resultado_conversa": "venda_fechada/follow_up_agendado/cliente_perdido/indefinido",
              "nivel_interesse_cliente": "alto/medio/baixo",
              "resumo_executivo": "O que aconteceu nesta ligação em 2-3 frases",
              "principal_objecao": "Principal objeção do cliente",
              "recomendacao_principal": "Principal sugestão para melhorar",
              "classificacao_ligacao": "A/B/C/D"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:]
            if analysis_text.endswith("```"):
                analysis_text = analysis_text[:-3]
            
            analysis = json.loads(analysis_text)
            analysis["vendedor"] = vendor_name or "Não identificado"
            analysis["arquivo_origem"] = file_name or "Não informado"
            analysis["timestamp_analise"] = datetime.now().isoformat()
            analysis["tipo_analise"] = "simplificada"
            
            return analysis
            
        except Exception as e:
            return {
                "erro": f"Falha completa na análise: {str(e)}",
                "vendedor": vendor_name or "Não identificado",
                "arquivo_origem": file_name or "Não informado",
                "timestamp_analise": datetime.now().isoformat(),
                "sentimento_geral": "indefinido",
                "performance_vendedor": "indefinido",
                "nota_vendedor": 0,
                "resumo_executivo": "Não foi possível analisar esta conversa automaticamente",
                "classificacao_ligacao": "D"
            }
    
    def analyze_multiple_conversations(self, transcriptions: List[Dict]) -> List[Dict]:
        """
        Analisa múltiplas conversas e extrai insights
        
        Args:
            transcriptions: Lista de transcrições com metadados
            
        Returns:
            Lista de análises completas
        """
        results = []
        total_transcriptions = len(transcriptions)
        
        print(f"🚀 Iniciando análise de {total_transcriptions} conversa(s)...")
        
        for i, transcription in enumerate(transcriptions, 1):
            print(f"\n📊 Analisando conversa {i}/{total_transcriptions}: {transcription.get('arquivo_origem', 'N/A')}")
            
            # Extrai nome do vendedor se não fornecido
            vendor_name = self.extract_vendor_name(transcription['texto'])
            
            # Analisa a conversa
            analysis = self.analyze_sales_conversation(
                transcription['texto'],
                vendor_name,
                transcription.get('arquivo_origem')
            )
            
            # Adiciona dados da transcrição original
            result = {
                "transcricao": transcription,
                "analise": analysis
            }
            
            results.append(result)
            print(f"✅ Análise concluída ({i}/{total_transcriptions})")
        
        print(f"\n🎉 Análise concluída! {len(results)} conversa(s) analisada(s).")
        return results

