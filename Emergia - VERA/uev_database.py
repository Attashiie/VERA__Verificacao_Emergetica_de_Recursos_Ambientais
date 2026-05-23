"""
Base de dados de UEVs (Transformidades / Unitary Emergy Values)
Valores padrão da literatura científica para análise emergética
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class UEVRecord:
    """Registro de UEV"""
    resource: str
    category: str
    uev_value: float
    unit: str
    source: str
    year: int
    notes: str = ""


class UEVDatabase:
    """Banco de dados de transformidades"""
    
    # Banco de dados padrão baseado em Odum (1996) e literatura
    DEFAULT_UEVS = [
        # Recursos Renováveis
        {
            'resource': 'Luz solar',
            'category': 'Renovável',
            'uev': 1.00e+00,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Vento',
            'category': 'Renovável',
            'uev': 1.50e+03,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Chuva (potencial gravitacional)',
            'category': 'Renovável',
            'uev': 2.79e+04,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Chuva (conteúdo químico)',
            'category': 'Renovável',
            'uev': 1.82e+04,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Calor geotérmico',
            'category': 'Renovável',
            'uev': 1.20e+04,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Madeira bruta',
            'category': 'Renovável',
            'uev': 3.49e+04,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Biomassa agrícola',
            'category': 'Renovável',
            'uev': 6.80e+04,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996,
            'notes': 'Conversão aproximada: 6800 sej/g = 1.55e6 sej/J'
        },
        {
            'resource': 'Ração animal (médio)',
            'category': 'Renovável',
            'uev': 1.20e+05,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        # Recursos Não-Renováveis
        {
            'resource': 'Gás natural',
            'category': 'Não-Renovável',
            'uev': 4.80e+04,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Petróleo bruto',
            'category': 'Não-Renovável',
            'uev': 5.40e+04,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Carvão mineral',
            'category': 'Não-Renovável',
            'uev': 3.98e+04,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Urânio',
            'category': 'Não-Renovável',
            'uev': 5.60e+06,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Fosfato (P)',
            'category': 'Não-Renovável',
            'uev': 1.92e+13,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Potássio (K)',
            'category': 'Não-Renovável',
            'uev': 9.65e+11,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        # Materiais Processados (Importados)
        {
            'resource': 'Eletricidade',
            'category': 'Importado',
            'uev': 1.60e+05,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996,
            'notes': 'Baseado em matriz energética média (hidro + termoelétricas)'
        },
        {
            'resource': 'Diesel/Gasolina refinados',
            'category': 'Importado',
            'uev': 1.20e+05,
            'unit': 'sej/J',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Aço',
            'category': 'Importado',
            'uev': 1.13e+09,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996,
            'notes': 'Aço estrutural; conversão: 1.13e9 sej/g = 2.6e7 sej/kg'
        },
        {
            'resource': 'Alumínio',
            'category': 'Importado',
            'uev': 1.76e+09,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Cobre',
            'category': 'Importado',
            'uev': 1.28e+09,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Cimento Portland',
            'category': 'Importado',
            'uev': 3.05e+08,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996,
            'notes': 'Conversão: 3.05e8 sej/g = 7.0e6 sej/kg'
        },
        {
            'resource': 'Cal virgem',
            'category': 'Importado',
            'uev': 2.94e+08,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Vidro',
            'category': 'Importado',
            'uev': 1.15e+08,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Água (processada)',
            'category': 'Importado',
            'uev': 3.10e+05,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996,
            'notes': 'Água purificada e entregue; 3.10e5 sej/g = 3.1e14 sej/L'
        },
        {
            'resource': 'Papel/Celulose',
            'category': 'Importado',
            'uev': 4.00e+07,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Fertilizante NPK (sintético)',
            'category': 'Importado',
            'uev': 1.40e+09,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        {
            'resource': 'Pesticida (genérico)',
            'category': 'Importado',
            'uev': 6.40e+10,
            'unit': 'sej/g',
            'source': 'Odum 1996',
            'year': 1996
        },
        # Serviços / Trabalho
        {
            'resource': 'Trabalho humano',
            'category': 'Serviço',
            'uev': 2.50e+06,
            'unit': 'sej/joule metabólico',
            'source': 'Odum 1996',
            'year': 1996,
            'notes': 'Baseado em metabolismo humano de ~1 kcal/min de trabalho'
        },
        # Valores Regionalizados (Exemplo)
        {
            'resource': 'Eletricidade (Brasil - Hidro)',
            'category': 'Importado',
            'uev': 1.20e+05,
            'unit': 'sej/J',
            'source': 'Adaptado para Brasil',
            'year': 2020,
            'notes': 'Baseado em matriz hidrotérmica brasileira'
        },
        {
            'resource': 'Água (Brasil - bacia úmida)',
            'category': 'Renovável',
            'uev': 2.50e+04,
            'unit': 'sej/J',
            'source': 'Adaptado para Brasil',
            'year': 2020,
            'notes': 'Regiões com alta precipitação'
        },
    ]
    
    def __init__(self, data: Optional[List[Dict]] = None):
        """Inicializa banco de dados"""
        if data is None:
            data = self.DEFAULT_UEVS
        self.data = data
    
    def get_uev(self, resource: str) -> Optional[float]:
        """Obtém UEV de um recurso por nome"""
        for record in self.data:
            if record['resource'].lower() == resource.lower():
                return record['uev']
        return None
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Busca UEVs por categoria"""
        return [r for r in self.data if r['category'].lower() == category.lower()]
    
    def search_by_name(self, query: str) -> List[Dict]:
        """Busca UEVs por nome (busca parcial)"""
        q = query.lower()
        return [r for r in self.data if q in r['resource'].lower()]
    
    def list_by_category(self) -> Dict[str, List[Dict]]:
        """Lista UEVs agrupadas por categoria"""
        grouped = {}
        for record in self.data:
            cat = record['category']
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(record)
        return grouped
    
    def add_record(self, record: Dict) -> None:
        """Adiciona novo registro"""
        self.data.append(record)
    
    def export_to_csv(self, filepath: str) -> None:
        """Exporta banco de dados para CSV"""
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['resource', 'category', 'uev', 'unit', 'source', 'year', 'notes'])
            writer.writeheader()
            writer.writerows(self.data)
    
    def export_to_json(self, filepath: str) -> None:
        """Exporta banco de dados para JSON"""
        import json
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def print_summary(self) -> None:
        """Imprime resumo do banco de dados"""
        grouped = self.list_by_category()
        
        print("\n" + "="*80)
        print("BANCO DE DADOS DE TRANSFORMIDADES (UEVs)")
        print("="*80)
        
        for category, records in grouped.items():
            print(f"\n{category.upper()} ({len(records)} registros)")
            print("-"*80)
            for r in records:
                print(f"  {r['resource']:<40} {r['uev']:.2e} {r['unit']}")
                if r.get('notes'):
                    print(f"    ℹ {r['notes']}")


def main():
    """Exemplo de uso do banco de dados"""
    # Cria banco de dados
    db = UEVDatabase()
    
    # Imprime resumo
    db.print_summary()
    
    # Busca específica
    print("\n" + "="*80)
    print("EXEMPLOS DE BUSCA")
    print("="*80)
    
    print("\n1. UEV de 'Eletricidade':")
    uev = db.get_uev('Eletricidade')
    print(f"   {uev:.2e} sej/J")
    
    print("\n2. Recursos com 'água':")
    results = db.search_by_name('água')
    for r in results:
        print(f"   - {r['resource']}: {r['uev']:.2e} {r['unit']}")
    
    print("\n3. Exportando banco de dados...")
    csv_path = r"c:\Users\vitor\OneDrive\Documentos\Facul_Projetos\Emergia - Backup\uevs_database.csv"
    json_path = r"c:\Users\vitor\OneDrive\Documentos\Facul_Projetos\Emergia - Backup\uevs_database.json"
    
    db.export_to_csv(csv_path)
    db.export_to_json(json_path)
    
    print(f"   [OK] CSV:  {csv_path}")
    print(f"   [OK] JSON: {json_path}")


if __name__ == "__main__":
    main()
