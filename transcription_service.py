"""
Serviço de Transcrição usando AssemblyAI
"""
import os
import requests
import time
from typing import Dict, Optional
from datetime import datetime


class AssemblyAITranscriptionService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"authorization": api_key}
        self.upload_url = "https://api.assemblyai.com/v2/upload"
        self.transcript_url = "https://api.assemblyai.com/v2/transcript"
    
    def upload_audio_file(self, audio_path: str) -> Optional[str]:
        """
        Faz upload do arquivo de áudio para AssemblyAI
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            URL do áudio no AssemblyAI ou None se falhar
        """
        try:
            print(f"📤 Fazendo upload de {os.path.basename(audio_path)}...")
            
            with open(audio_path, "rb") as f:
                response = requests.post(self.upload_url, headers=self.headers, data=f)
            
            if response.status_code == 200:
                upload_data = response.json()
                print(f"✅ Upload concluído para {os.path.basename(audio_path)}")
                return upload_data["upload_url"]
            else:
                print(f"❌ Erro no upload: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao fazer upload: {str(e)}")
            return None
    
    def submit_transcription_job(self, audio_url: str, language_code: str = "pt") -> Optional[str]:
        """
        Submete job de transcrição para AssemblyAI
        
        Args:
            audio_url: URL do áudio no AssemblyAI
            language_code: Código do idioma (padrão: "pt" para português)
            
        Returns:
            ID do job de transcrição ou None se falhar
        """
        try:
            print("📝 Submetendo job de transcrição...")
            
            json_data = {
                "audio_url": audio_url,
                "language_code": language_code,
                "speaker_labels": True,  # Identifica diferentes falantes
                "auto_chapters": False,
                "summarization": False,
                "sentiment_analysis": False,  # Faremos nossa própria análise
                "entity_detection": False
            }
            
            response = requests.post(self.transcript_url, headers=self.headers, json=json_data)
            
            if response.status_code == 200:
                job_data = response.json()
                job_id = job_data["id"]
                print(f"✅ Job de transcrição submetido! ID: {job_id}")
                return job_id
            else:
                print(f"❌ Erro ao submeter job: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao submeter job de transcrição: {str(e)}")
            return None
    
    def get_transcription_result(self, job_id: str, max_wait_time: int = 600) -> Optional[Dict]:
        """
        Aguarda e obtém o resultado da transcrição
        
        Args:
            job_id: ID do job de transcrição
            max_wait_time: Tempo máximo de espera em segundos (padrão: 10 minutos)
            
        Returns:
            Dicionário com resultado da transcrição ou None se falhar
        """
        try:
            print(f"⏳ Aguardando resultado da transcrição (Job ID: {job_id})...")
            
            polling_endpoint = f"{self.transcript_url}/{job_id}"
            start_time = time.time()
            
            while True:
                # Verifica se excedeu o tempo limite
                if time.time() - start_time > max_wait_time:
                    print(f"❌ Timeout: Transcrição demorou mais que {max_wait_time} segundos")
                    return None
                
                polling_response = requests.get(polling_endpoint, headers=self.headers)
                
                if polling_response.status_code != 200:
                    print(f"❌ Erro ao verificar status: {polling_response.status_code}")
                    return None
                
                transcription_result = polling_response.json()
                status = transcription_result["status"]
                
                if status == "completed":
                    print("✅ Transcrição concluída!")
                    return {
                        "text": transcription_result["text"],
                        "confidence": transcription_result.get("confidence", 0),
                        "audio_duration": transcription_result.get("audio_duration", 0),
                        "words": transcription_result.get("words", []),
                        "utterances": transcription_result.get("utterances", []),  # Para identificar falantes
                        "language_code": transcription_result.get("language_code", "pt")
                    }
                elif status == "error":
                    error_msg = transcription_result.get("error", "Erro desconhecido")
                    print(f"❌ Erro na transcrição: {error_msg}")
                    return None
                else:
                    print(f"Status: {status}. Aguardando...")
                    time.sleep(5)  # Espera 5 segundos antes de verificar novamente
                    
        except Exception as e:
            print(f"❌ Erro ao obter resultado da transcrição: {str(e)}")
            return None
    
    def transcribe_audio_file(self, audio_path: str, language_code: str = "pt") -> Optional[Dict]:
        """
        Processo completo de transcrição de um arquivo de áudio
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            language_code: Código do idioma
            
        Returns:
            Dicionário com resultado da transcrição e metadados
        """
        try:
            # 1. Upload do arquivo
            audio_url = self.upload_audio_file(audio_path)
            if not audio_url:
                return None
            
            # 2. Submeter job de transcrição
            job_id = self.submit_transcription_job(audio_url, language_code)
            if not job_id:
                return None
            
            # 3. Aguardar e obter resultado
            transcription_data = self.get_transcription_result(job_id)
            if not transcription_data:
                return None
            
            # 4. Adicionar metadados
            result = {
                "arquivo_origem": os.path.basename(audio_path),
                "caminho_completo": audio_path,
                "texto": transcription_data["text"],
                "confianca": transcription_data["confidence"],
                "duracao_audio": transcription_data["audio_duration"],
                "palavras": transcription_data["words"],
                "utterances": transcription_data["utterances"],
                "idioma": transcription_data["language_code"],
                "timestamp_transcricao": datetime.now().isoformat(),
                "job_id": job_id
            }
            
            print(f"✅ Transcrição completa para {os.path.basename(audio_path)}")
            return result
            
        except Exception as e:
            print(f"❌ Erro no processo de transcrição: {str(e)}")
            return None
    
    def transcribe_multiple_files(self, audio_files: list, language_code: str = "pt") -> list:
        """
        Transcreve múltiplos arquivos de áudio
        
        Args:
            audio_files: Lista de caminhos para arquivos de áudio
            language_code: Código do idioma
            
        Returns:
            Lista de resultados de transcrição
        """
        results = []
        total_files = len(audio_files)
        
        print(f"🚀 Iniciando transcrição de {total_files} arquivo(s)...")
        
        for i, audio_path in enumerate(audio_files, 1):
            print(f"\n📊 Processando arquivo {i}/{total_files}: {os.path.basename(audio_path)}")
            
            result = self.transcribe_audio_file(audio_path, language_code)
            if result:
                results.append(result)
                print(f"✅ Sucesso ({i}/{total_files})")
            else:
                print(f"❌ Falha ({i}/{total_files})")
        
        print(f"\n🎉 Transcrição concluída! {len(results)}/{total_files} arquivo(s) processado(s) com sucesso.")
        return results

