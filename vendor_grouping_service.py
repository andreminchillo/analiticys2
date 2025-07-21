"""
Serviço de Agrupamento e Análise por Vendedor
"""
from typing import Dict, List
from collections import defaultdict
import statistics
from datetime import datetime


class VendorGroupingService:
    def __init__(self):
        pass
    
    def group_conversations_by_vendor(self, analyzed_conversations: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa conversas analisadas por vendedor
        
        Args:
            analyzed_conversations: Lista de conversas analisadas
            
        Returns:
            Dicionário com vendedores como chaves e suas conversas como valores
        """
        vendor_groups = defaultdict(list)
        
        for conversation in analyzed_conversations:
            analysis = conversation.get('analise', {})
            vendor_name = analysis.get('vendedor', 'Não identificado')
            
            # Normaliza o nome do vendedor
            vendor_name = self._normalize_vendor_name(vendor_name)
            
            vendor_groups[vendor_name].append(conversation)
        
        return dict(vendor_groups)
    
    def _normalize_vendor_name(self, vendor_name: str) -> str:
        """
        Normaliza o nome do vendedor para agrupamento consistente
        """
        if not vendor_name or vendor_name.lower() in ['não identificado', 'não informado', 'desconhecido']:
            return 'Não identificado'
        
        # Remove espaços extras e capitaliza
        return vendor_name.strip().title()
    
    def calculate_vendor_statistics(self, vendor_conversations: List[Dict]) -> Dict:
        """
        Calcula estatísticas consolidadas para um vendedor
        
        Args:
            vendor_conversations: Lista de conversas do vendedor
            
        Returns:
            Dicionário com estatísticas do vendedor
        """
        if not vendor_conversations:
            return {}
        
        # Extrai dados das análises
        notas = []
        sentimentos_positivos = 0
        vendas_fechadas = 0
        follow_ups = 0
        clientes_perdidos = 0
        classificacoes = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        todas_objecoes = []
        todos_pontos_fortes = []
        todos_pontos_melhoria = []
        todas_recomendacoes = []
        produtos_mencionados = []
        
        for conversation in vendor_conversations:
            analysis = conversation.get('analise', {})
            
            # Notas
            nota = analysis.get('nota_vendedor', 0)
            if isinstance(nota, (int, float)) and nota > 0:
                notas.append(nota)
            
            # Sentimentos
            if analysis.get('sentimento_geral') == 'positivo':
                sentimentos_positivos += 1
            
            # Resultados
            resultado = analysis.get('resultado_conversa', '')
            if 'venda_fechada' in resultado:
                vendas_fechadas += 1
            elif 'follow_up' in resultado:
                follow_ups += 1
            elif 'perdido' in resultado:
                clientes_perdidos += 1
            
            # Classificações
            classificacao = analysis.get('classificacao_ligacao', 'D')
            if classificacao in classificacoes:
                classificacoes[classificacao] += 1
            
            # Coleta dados qualitativos
            if analysis.get('objecoes_cliente'):
                todas_objecoes.extend(analysis['objecoes_cliente'])
            
            if analysis.get('pontos_fortes'):
                todos_pontos_fortes.extend(analysis['pontos_fortes'])
            
            if analysis.get('pontos_melhoria'):
                todos_pontos_melhoria.extend(analysis['pontos_melhoria'])
            
            if analysis.get('recomendacoes_especificas'):
                todas_recomendacoes.extend(analysis['recomendacoes_especificas'])
            
            if analysis.get('produtos_mencionados'):
                produtos_mencionados.extend(analysis['produtos_mencionados'])
        
        total_conversas = len(vendor_conversations)
        
        # Calcula estatísticas
        stats = {
            'total_conversas': total_conversas,
            'nota_media': round(statistics.mean(notas), 1) if notas else 0,
            'nota_mediana': round(statistics.median(notas), 1) if notas else 0,
            'melhor_nota': max(notas) if notas else 0,
            'pior_nota': min(notas) if notas else 0,
            
            'sentimentos_positivos': sentimentos_positivos,
            'percentual_sentimentos_positivos': round((sentimentos_positivos / total_conversas) * 100, 1),
            
            'vendas_fechadas': vendas_fechadas,
            'follow_ups_agendados': follow_ups,
            'clientes_perdidos': clientes_perdidos,
            'taxa_conversao': round((vendas_fechadas / total_conversas) * 100, 1),
            
            'classificacoes': classificacoes,
            'percentual_a_b': round(((classificacoes['A'] + classificacoes['B']) / total_conversas) * 100, 1),
            
            'objecoes_mais_comuns': self._get_most_common_items(todas_objecoes, 5),
            'pontos_fortes_principais': self._get_most_common_items(todos_pontos_fortes, 5),
            'areas_melhoria_principais': self._get_most_common_items(todos_pontos_melhoria, 5),
            'recomendacoes_principais': self._get_most_common_items(todas_recomendacoes, 5),
            'produtos_mais_vendidos': self._get_most_common_items(produtos_mencionados, 5),
            
            'timestamp_calculo': datetime.now().isoformat()
        }
        
        return stats
    
    def _get_most_common_items(self, items_list: List[str], top_n: int = 5) -> List[Dict]:
        """
        Retorna os itens mais comuns de uma lista
        """
        if not items_list:
            return []
        
        # Conta frequência dos itens
        frequency = defaultdict(int)
        for item in items_list:
            if item and isinstance(item, str):
                frequency[item.strip().lower()] += 1
        
        # Ordena por frequência
        sorted_items = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Retorna top N com formatação
        result = []
        for item, count in sorted_items[:top_n]:
            result.append({
                'item': item.title(),
                'frequencia': count,
                'percentual': round((count / len(items_list)) * 100, 1)
            })
        
        return result
    
    def generate_vendor_insights(self, vendor_name: str, vendor_conversations: List[Dict], vendor_stats: Dict) -> Dict:
        """
        Gera insights consolidados para um vendedor
        
        Args:
            vendor_name: Nome do vendedor
            vendor_conversations: Lista de conversas do vendedor
            vendor_stats: Estatísticas calculadas do vendedor
            
        Returns:
            Dicionário com insights consolidados
        """
        # Determina nível de performance baseado na nota média
        nota_media = vendor_stats.get('nota_media', 0)
        if nota_media >= 8:
            nivel_performance = 'Excelente'
        elif nota_media >= 6:
            nivel_performance = 'Bom'
        elif nota_media >= 4:
            nivel_performance = 'Regular'
        else:
            nivel_performance = 'Precisa Melhorar'
        
        # Determina prioridades de treinamento
        prioridades_treinamento = []
        
        if vendor_stats.get('taxa_conversao', 0) < 20:
            prioridades_treinamento.append('Técnicas de fechamento')
        
        if vendor_stats.get('percentual_sentimentos_positivos', 0) < 60:
            prioridades_treinamento.append('Relacionamento com cliente')
        
        if vendor_stats.get('percentual_a_b', 0) < 50:
            prioridades_treinamento.append('Qualidade geral das ligações')
        
        # Identifica pontos fortes e fracos
        pontos_fortes = [item['item'] for item in vendor_stats.get('pontos_fortes_principais', [])[:3]]
        areas_melhoria = [item['item'] for item in vendor_stats.get('areas_melhoria_principais', [])[:3]]
        
        insights = {
            'vendedor': vendor_name,
            'nivel_performance': nivel_performance,
            'nota_geral': nota_media,
            'total_ligacoes': vendor_stats.get('total_conversas', 0),
            
            'pontos_fortes_principais': pontos_fortes,
            'areas_melhoria_principais': areas_melhoria,
            'prioridades_treinamento': prioridades_treinamento,
            
            'taxa_conversao': vendor_stats.get('taxa_conversao', 0),
            'taxa_sentimento_positivo': vendor_stats.get('percentual_sentimentos_positivos', 0),
            'taxa_ligacoes_qualidade': vendor_stats.get('percentual_a_b', 0),
            
            'objecoes_mais_enfrentadas': [item['item'] for item in vendor_stats.get('objecoes_mais_comuns', [])[:3]],
            'produtos_mais_trabalhados': [item['item'] for item in vendor_stats.get('produtos_mais_vendidos', [])[:3]],
            
            'recomendacao_principal': self._generate_main_recommendation(vendor_stats),
            'proximos_passos': self._generate_next_steps(vendor_stats),
            
            'timestamp_insights': datetime.now().isoformat()
        }
        
        return insights
    
    def _generate_main_recommendation(self, vendor_stats: Dict) -> str:
        """
        Gera recomendação principal baseada nas estatísticas
        """
        nota_media = vendor_stats.get('nota_media', 0)
        taxa_conversao = vendor_stats.get('taxa_conversao', 0)
        sentimentos_positivos = vendor_stats.get('percentual_sentimentos_positivos', 0)
        
        if nota_media < 5:
            return "Foco em treinamento básico de vendas e atendimento ao cliente"
        elif taxa_conversao < 15:
            return "Desenvolver técnicas de fechamento e identificação de oportunidades"
        elif sentimentos_positivos < 50:
            return "Melhorar relacionamento e comunicação com clientes"
        else:
            return "Manter bom desempenho e focar em casos específicos de melhoria"
    
    def _generate_next_steps(self, vendor_stats: Dict) -> List[str]:
        """
        Gera próximos passos baseados nas estatísticas
        """
        steps = []
        
        if vendor_stats.get('taxa_conversao', 0) < 20:
            steps.append("Participar de treinamento de técnicas de fechamento")
        
        if vendor_stats.get('percentual_sentimentos_positivos', 0) < 60:
            steps.append("Praticar escuta ativa e empatia com clientes")
        
        areas_melhoria = vendor_stats.get('areas_melhoria_principais', [])
        if areas_melhoria:
            steps.append(f"Trabalhar especificamente em: {areas_melhoria[0]['item']}")
        
        if vendor_stats.get('nota_media', 0) >= 7:
            steps.append("Compartilhar boas práticas com a equipe")
        
        if not steps:
            steps.append("Manter o bom desempenho atual")
        
        return steps[:4]  # Máximo 4 próximos passos
    
    def process_all_vendors(self, analyzed_conversations: List[Dict]) -> Dict:
        """
        Processa todos os vendedores e gera relatório consolidado
        
        Args:
            analyzed_conversations: Lista de todas as conversas analisadas
            
        Returns:
            Dicionário com dados consolidados de todos os vendedores
        """
        print("👥 Agrupando conversas por vendedor...")
        
        # Agrupa por vendedor
        vendor_groups = self.group_conversations_by_vendor(analyzed_conversations)
        
        vendor_reports = {}
        
        for vendor_name, conversations in vendor_groups.items():
            print(f"📊 Processando vendedor: {vendor_name} ({len(conversations)} conversas)")
            
            # Calcula estatísticas
            stats = self.calculate_vendor_statistics(conversations)
            
            # Gera insights
            insights = self.generate_vendor_insights(vendor_name, conversations, stats)
            
            vendor_reports[vendor_name] = {
                'conversas': conversations,
                'estatisticas': stats,
                'insights': insights
            }
        
        # Gera estatísticas gerais da equipe
        team_stats = self._calculate_team_statistics(vendor_reports)
        
        result = {
            'vendedores': vendor_reports,
            'estatisticas_equipe': team_stats,
            'total_vendedores': len(vendor_reports),
            'total_conversas': len(analyzed_conversations),
            'timestamp_processamento': datetime.now().isoformat()
        }
        
        print(f"✅ Processamento concluído: {len(vendor_reports)} vendedor(es), {len(analyzed_conversations)} conversa(s)")
        
        return result
    
    def _calculate_team_statistics(self, vendor_reports: Dict) -> Dict:
        """
        Calcula estatísticas consolidadas da equipe
        """
        if not vendor_reports:
            return {}
        
        all_stats = [report['estatisticas'] for report in vendor_reports.values()]
        
        # Médias da equipe
        notas_medias = [stats.get('nota_media', 0) for stats in all_stats if stats.get('nota_media', 0) > 0]
        taxas_conversao = [stats.get('taxa_conversao', 0) for stats in all_stats]
        sentimentos_positivos = [stats.get('percentual_sentimentos_positivos', 0) for stats in all_stats]
        
        team_stats = {
            'nota_media_equipe': round(statistics.mean(notas_medias), 1) if notas_medias else 0,
            'taxa_conversao_media': round(statistics.mean(taxas_conversao), 1) if taxas_conversao else 0,
            'sentimento_positivo_medio': round(statistics.mean(sentimentos_positivos), 1) if sentimentos_positivos else 0,
            
            'melhor_vendedor': self._find_best_vendor(vendor_reports),
            'vendedor_precisa_atencao': self._find_vendor_needs_attention(vendor_reports),
            
            'total_vendas_fechadas': sum(stats.get('vendas_fechadas', 0) for stats in all_stats),
            'total_follow_ups': sum(stats.get('follow_ups_agendados', 0) for stats in all_stats),
            'total_clientes_perdidos': sum(stats.get('clientes_perdidos', 0) for stats in all_stats),
        }
        
        return team_stats
    
    def _find_best_vendor(self, vendor_reports: Dict) -> str:
        """
        Identifica o melhor vendedor baseado na nota média
        """
        best_vendor = None
        best_score = 0
        
        for vendor_name, report in vendor_reports.items():
            nota_media = report['estatisticas'].get('nota_media', 0)
            if nota_media > best_score:
                best_score = nota_media
                best_vendor = vendor_name
        
        return best_vendor or 'Não identificado'
    
    def _find_vendor_needs_attention(self, vendor_reports: Dict) -> str:
        """
        Identifica o vendedor que mais precisa de atenção
        """
        worst_vendor = None
        worst_score = 10
        
        for vendor_name, report in vendor_reports.items():
            nota_media = report['estatisticas'].get('nota_media', 10)
            if nota_media < worst_score:
                worst_score = nota_media
                worst_vendor = vendor_name
        
        return worst_vendor or 'Não identificado'

