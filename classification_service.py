"""
Serviço de Classificação e Pontuação de Ligações
"""
from typing import Dict, List
from datetime import datetime


class CallClassificationService:
    def __init__(self):
        # Critérios de pontuação
        self.scoring_criteria = {
            'sentimento_geral': {
                'positivo': 3,
                'neutro': 2,
                'negativo': 1
            },
            'resultado_conversa': {
                'venda_fechada': 4,
                'follow_up_agendado': 3,
                'indefinido': 2,
                'cliente_perdido': 1
            },
            'nivel_interesse_cliente': {
                'alto': 3,
                'medio': 2,
                'baixo': 1
            },
            'satisfacao_cliente': {
                'alta': 3,
                'media': 2,
                'baixa': 1
            },
            'performance_vendedor': {
                'excelente': 4,
                'boa': 3,
                'regular': 2,
                'ruim': 1
            }
        }
    
    def classify_call(self, analysis: Dict) -> Dict:
        """
        Classifica uma ligação baseada na análise
        
        Args:
            analysis: Dicionário com análise da conversa
            
        Returns:
            Dicionário com classificação e pontuação detalhada
        """
        # Calcula pontuação por critério
        scores = {}
        total_score = 0
        max_possible_score = 0
        
        for criterion, values in self.scoring_criteria.items():
            analysis_value = analysis.get(criterion, '').lower()
            score = values.get(analysis_value, 0)
            scores[criterion] = {
                'valor': analysis_value,
                'pontos': score,
                'maximo': max(values.values())
            }
            total_score += score
            max_possible_score += max(values.values())
        
        # Calcula pontuação percentual
        percentage_score = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        # Determina classificação (A, B, C, D)
        if percentage_score >= 80:
            classification = 'A'
            classification_desc = 'Excelente'
        elif percentage_score >= 65:
            classification = 'B'
            classification_desc = 'Boa'
        elif percentage_score >= 50:
            classification = 'C'
            classification_desc = 'Regular'
        else:
            classification = 'D'
            classification_desc = 'Precisa Melhorar'
        
        # Determina nota do vendedor baseada em múltiplos fatores
        vendor_score = self._calculate_vendor_score(analysis)
        
        # Identifica pontos críticos
        critical_points = self._identify_critical_points(analysis, scores)
        
        # Gera recomendações específicas
        recommendations = self._generate_call_recommendations(analysis, scores)
        
        result = {
            'classificacao': classification,
            'classificacao_descricao': classification_desc,
            'pontuacao_total': total_score,
            'pontuacao_maxima': max_possible_score,
            'pontuacao_percentual': round(percentage_score, 1),
            'nota_vendedor': vendor_score,
            'pontuacao_detalhada': scores,
            'pontos_criticos': critical_points,
            'recomendacoes_classificacao': recommendations,
            'timestamp_classificacao': datetime.now().isoformat()
        }
        
        return result
    
    def _calculate_vendor_score(self, analysis: Dict) -> float:
        """
        Calcula nota específica do vendedor (1-10)
        """
        # Fatores que influenciam a nota do vendedor
        factors = {
            'performance_vendedor': {
                'excelente': 10,
                'boa': 7.5,
                'regular': 5,
                'ruim': 2.5
            },
            'resultado_conversa': {
                'venda_fechada': 3,
                'follow_up_agendado': 2,
                'indefinido': 1,
                'cliente_perdido': 0
            },
            'sentimento_geral': {
                'positivo': 2,
                'neutro': 1,
                'negativo': 0
            }
        }
        
        base_score = factors['performance_vendedor'].get(
            analysis.get('performance_vendedor', '').lower(), 5
        )
        
        # Ajustes baseados em resultado e sentimento
        result_bonus = factors['resultado_conversa'].get(
            analysis.get('resultado_conversa', '').lower(), 0
        )
        
        sentiment_bonus = factors['sentimento_geral'].get(
            analysis.get('sentimento_geral', '').lower(), 0
        )
        
        # Penalidades por problemas específicos
        penalties = 0
        
        # Penalidade por oportunidades perdidas
        if analysis.get('oportunidades_perdidas') and len(analysis['oportunidades_perdidas']) > 2:
            penalties += 0.5
        
        # Penalidade por muitas objeções não tratadas
        if analysis.get('objecoes_cliente') and len(analysis['objecoes_cliente']) > 3:
            penalties += 0.5
        
        # Penalidade por qualidade ruim da ligação
        if analysis.get('qualidade_ligacao', '').lower() == 'ruim':
            penalties += 1
        
        final_score = base_score + result_bonus + sentiment_bonus - penalties
        
        # Garante que a nota está entre 1 e 10
        return max(1, min(10, round(final_score, 1)))
    
    def _identify_critical_points(self, analysis: Dict, scores: Dict) -> List[str]:
        """
        Identifica pontos críticos da ligação
        """
        critical_points = []
        
        # Verifica pontuações baixas
        for criterion, score_data in scores.items():
            if score_data['pontos'] <= 1:
                critical_points.append(f"Baixa pontuação em {criterion}: {score_data['valor']}")
        
        # Verifica problemas específicos
        if analysis.get('resultado_conversa', '').lower() == 'cliente_perdido':
            critical_points.append("Cliente perdido - analisar causas")
        
        if analysis.get('sentimento_geral', '').lower() == 'negativo':
            critical_points.append("Sentimento negativo do cliente")
        
        if analysis.get('nivel_interesse_cliente', '').lower() == 'baixo':
            critical_points.append("Baixo interesse do cliente")
        
        # Verifica oportunidades perdidas
        oportunidades = analysis.get('oportunidades_perdidas', [])
        if oportunidades and len(oportunidades) > 2:
            critical_points.append(f"Múltiplas oportunidades perdidas ({len(oportunidades)})")
        
        # Verifica objeções não tratadas
        objecoes = analysis.get('objecoes_cliente', [])
        if objecoes and len(objecoes) > 2:
            critical_points.append(f"Múltiplas objeções do cliente ({len(objecoes)})")
        
        return critical_points[:5]  # Máximo 5 pontos críticos
    
    def _generate_call_recommendations(self, analysis: Dict, scores: Dict) -> List[str]:
        """
        Gera recomendações específicas para a ligação
        """
        recommendations = []
        
        # Recomendações baseadas em pontuações baixas
        for criterion, score_data in scores.items():
            if score_data['pontos'] <= 1:
                if criterion == 'sentimento_geral':
                    recommendations.append("Melhorar abordagem e empatia com o cliente")
                elif criterion == 'resultado_conversa':
                    recommendations.append("Trabalhar técnicas de fechamento e follow-up")
                elif criterion == 'nivel_interesse_cliente':
                    recommendations.append("Desenvolver melhor descoberta de necessidades")
                elif criterion == 'satisfacao_cliente':
                    recommendations.append("Focar em atendimento e resolução de problemas")
                elif criterion == 'performance_vendedor':
                    recommendations.append("Treinamento geral em técnicas de vendas")
        
        # Recomendações específicas baseadas na análise
        if analysis.get('momento_critico'):
            recommendations.append("Analisar momento crítico identificado na conversa")
        
        if analysis.get('oportunidades_perdidas'):
            recommendations.append("Revisar oportunidades perdidas para aprendizado")
        
        # Recomendações baseadas em pontos fortes
        pontos_fortes = analysis.get('pontos_fortes', [])
        if pontos_fortes:
            recommendations.append(f"Manter pontos fortes: {', '.join(pontos_fortes[:2])}")
        
        return recommendations[:4]  # Máximo 4 recomendações
    
    def classify_multiple_calls(self, analyzed_conversations: List[Dict]) -> List[Dict]:
        """
        Classifica múltiplas ligações
        
        Args:
            analyzed_conversations: Lista de conversas analisadas
            
        Returns:
            Lista de conversas com classificação adicionada
        """
        classified_calls = []
        
        print(f"🏷️ Classificando {len(analyzed_conversations)} ligação(ões)...")
        
        for i, conversation in enumerate(analyzed_conversations, 1):
            analysis = conversation.get('analise', {})
            
            # Classifica a ligação
            classification = self.classify_call(analysis)
            
            # Adiciona classificação à conversa
            conversation_with_classification = conversation.copy()
            conversation_with_classification['classificacao'] = classification
            
            classified_calls.append(conversation_with_classification)
            
            print(f"✅ Ligação {i} classificada: {classification['classificacao']} (Nota: {classification['nota_vendedor']})")
        
        print(f"🎉 Classificação concluída!")
        return classified_calls
    
    def generate_classification_summary(self, classified_calls: List[Dict]) -> Dict:
        """
        Gera resumo das classificações
        
        Args:
            classified_calls: Lista de ligações classificadas
            
        Returns:
            Dicionário com resumo das classificações
        """
        if not classified_calls:
            return {}
        
        # Conta classificações
        classifications = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        total_score = 0
        vendor_scores = []
        
        for call in classified_calls:
            classification_data = call.get('classificacao', {})
            
            # Conta classificação
            classification = classification_data.get('classificacao', 'D')
            if classification in classifications:
                classifications[classification] += 1
            
            # Soma pontuações
            total_score += classification_data.get('pontuacao_percentual', 0)
            vendor_scores.append(classification_data.get('nota_vendedor', 0))
        
        total_calls = len(classified_calls)
        
        # Calcula estatísticas
        summary = {
            'total_ligacoes': total_calls,
            'distribuicao_classificacoes': classifications,
            'percentual_a_b': round(((classifications['A'] + classifications['B']) / total_calls) * 100, 1),
            'percentual_c_d': round(((classifications['C'] + classifications['D']) / total_calls) * 100, 1),
            
            'pontuacao_media': round(total_score / total_calls, 1) if total_calls > 0 else 0,
            'nota_media_vendedores': round(sum(vendor_scores) / len(vendor_scores), 1) if vendor_scores else 0,
            
            'melhor_ligacao': self._find_best_call(classified_calls),
            'pior_ligacao': self._find_worst_call(classified_calls),
            
            'pontos_criticos_comuns': self._find_common_critical_points(classified_calls),
            'recomendacoes_gerais': self._generate_general_recommendations(classifications, total_calls),
            
            'timestamp_resumo': datetime.now().isoformat()
        }
        
        return summary
    
    def _find_best_call(self, classified_calls: List[Dict]) -> Dict:
        """
        Encontra a melhor ligação
        """
        best_call = None
        best_score = 0
        
        for call in classified_calls:
            classification = call.get('classificacao', {})
            score = classification.get('pontuacao_percentual', 0)
            
            if score > best_score:
                best_score = score
                best_call = {
                    'arquivo': call.get('analise', {}).get('arquivo_origem', 'N/A'),
                    'vendedor': call.get('analise', {}).get('vendedor', 'N/A'),
                    'pontuacao': score,
                    'classificacao': classification.get('classificacao', 'N/A')
                }
        
        return best_call or {}
    
    def _find_worst_call(self, classified_calls: List[Dict]) -> Dict:
        """
        Encontra a pior ligação
        """
        worst_call = None
        worst_score = 100
        
        for call in classified_calls:
            classification = call.get('classificacao', {})
            score = classification.get('pontuacao_percentual', 100)
            
            if score < worst_score:
                worst_score = score
                worst_call = {
                    'arquivo': call.get('analise', {}).get('arquivo_origem', 'N/A'),
                    'vendedor': call.get('analise', {}).get('vendedor', 'N/A'),
                    'pontuacao': score,
                    'classificacao': classification.get('classificacao', 'N/A')
                }
        
        return worst_call or {}
    
    def _find_common_critical_points(self, classified_calls: List[Dict]) -> List[str]:
        """
        Encontra pontos críticos mais comuns
        """
        all_critical_points = []
        
        for call in classified_calls:
            classification = call.get('classificacao', {})
            critical_points = classification.get('pontos_criticos', [])
            all_critical_points.extend(critical_points)
        
        # Conta frequência
        from collections import Counter
        point_counts = Counter(all_critical_points)
        
        # Retorna os 5 mais comuns
        common_points = []
        for point, count in point_counts.most_common(5):
            common_points.append(f"{point} ({count} ocorrências)")
        
        return common_points
    
    def _generate_general_recommendations(self, classifications: Dict, total_calls: int) -> List[str]:
        """
        Gera recomendações gerais baseadas na distribuição de classificações
        """
        recommendations = []
        
        # Percentuais
        percent_a = (classifications['A'] / total_calls) * 100
        percent_d = (classifications['D'] / total_calls) * 100
        percent_a_b = ((classifications['A'] + classifications['B']) / total_calls) * 100
        
        if percent_d > 30:
            recommendations.append("Urgente: Mais de 30% das ligações precisam de melhoria significativa")
        
        if percent_a_b < 50:
            recommendations.append("Foco em treinamento geral da equipe - menos de 50% das ligações são boas")
        
        if percent_a < 20:
            recommendations.append("Desenvolver práticas de excelência - poucas ligações excelentes")
        
        if percent_a > 40:
            recommendations.append("Equipe performando bem - identificar e replicar boas práticas")
        
        if not recommendations:
            recommendations.append("Performance equilibrada - manter padrão atual")
        
        return recommendations

