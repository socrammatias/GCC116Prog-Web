# Em agenda/templatetags/tempo_restante.py

from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def formatar_tempo_restante(data_fim):
    """
    Calcula e formata a diferença entre data_fim e o tempo atual.
    Retorna uma string como 'Faltam X dias e Y horas' ou 'Vencido há Z horas'.
    """
    if data_fim is None:
        return ""

    diferenca = data_fim - timezone.now()
    
    if diferenca.total_seconds() <= 0:
        # Tarefa Vencida
        passado = diferenca * -1
        total_horas = int(passado.total_seconds() // 3600)
        
        if total_horas > 48:
            dias_vencidos = int(total_horas // 24)
            return f"❌ Vencida há {dias_vencidos} dias"
        elif total_horas > 0:
            return f"❌ Vencida há {total_horas} horas"
        else:
             return "❌ VENCIDA AGORA"
    
    # Tarefa no Futuro
    total_segundos = diferenca.total_seconds()
    
    # Cálculo:
    dias = int(total_segundos // 86400)
    total_segundos -= dias * 86400
    
    horas = int(total_segundos // 3600)
    total_segundos -= horas * 3600
    
    minutos = int(total_segundos // 60)
    
    partes = []
    if dias > 0:
        partes.append(f"{dias} dia{'s' if dias > 1 else ''}")
    if horas > 0:
        partes.append(f"{horas} hora{'s' if horas > 1 else ''}")
    if minutos > 0 and dias == 0 and horas == 0:
        partes.append(f"{minutos} minuto{'s' if minutos > 1 else ''}")
        
    if not partes:
        return "⏳ Vence em breve..."
        
    return f"⏳ Faltam {', '.join(partes)}"