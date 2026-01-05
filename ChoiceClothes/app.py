from flask import Flask, render_template, request
import rdflib

app = Flask(__name__, template_folder='templates')

# Загрузка онтологии
graph = rdflib.Graph()
graph.parse("ChoiceClothes.rdf", format="xml")
print("✅ Онтология одежды загружена успешно!")

def get_all_clothing_items():
    """Получить все элементы одежды"""
    print("\n🔍 ПОИСК ЭЛЕМЕНТОВ ОДЕЖДЫ...")
    
    query = """
    PREFIX cl: <http://www.semanticweb.org/user1/ontologies/2025/8/clothing#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?item ?name ?brand ?type
    WHERE {
        ?item cl:Название ?name ;
              cl:Бренд ?brand .
        ?item a ?type .
        ?type rdfs:subClassOf* cl:ЭлементОдежды .
    }
    ORDER BY ?name
    """
    
    try:
        qres = graph.query(query)
        items = []
        
        for row in qres:
            type_name = str(row["type"]).split("#")[-1] if "#" in str(row["type"]) else str(row["type"]).split("/")[-1]
            items.append({
                "name": str(row["name"]),
                "brand": str(row["brand"]),
                "type": type_name
            })
            print(f"  ✅ Найден: {row['name']} ({row['brand']})")
        
        print(f"📊 Всего найдено элементов одежды: {len(items)}")
        return items
        
    except Exception as e:
        print(f"❌ Ошибка в get_all_clothing_items: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_all_seasons():
    """Получить все сезоны"""
    print("\n🔍 ПОИСК СЕЗОНОВ...")
    
    query = """
    PREFIX cl: <http://www.semanticweb.org/user1/ontologies/2025/8/clothing#>
    SELECT DISTINCT ?season
    WHERE {
        ?season a cl:Сезон .
    }
    ORDER BY ?season
    """
    
    try:
        qres = graph.query(query)
        seasons = []
        
        for row in qres:
            season_name = str(row["season"]).split("#")[-1] if "#" in str(row["season"]) else str(row["season"]).split("/")[-1]
            seasons.append({
                "name": season_name
            })
            print(f"  ✅ Найден сезон: {season_name}")
        
        print(f"📊 Всего найдено сезонов: {len(seasons)}")
        return seasons
        
    except Exception as e:
        print(f"❌ Ошибка в get_all_seasons: {e}")
        return []

def get_all_precipitation():
    """Получить все типы осадков"""
    print("\n🔍 ПОИСК ТИПОВ ОСАДКОВ...")
    
    query = """
    PREFIX cl: <http://www.semanticweb.org/user1/ontologies/2025/8/clothing#>
    SELECT DISTINCT ?precipitation
    WHERE {
        ?precipitation a cl:Осадки .
    }
    ORDER BY ?precipitation
    """
    
    try:
        qres = graph.query(query)
        precipitations = []
        
        for row in qres:
            prec_name = str(row["precipitation"]).split("#")[-1] if "#" in str(row["precipitation"]) else str(row["precipitation"]).split("/")[-1]
            precipitations.append({
                "name": prec_name
            })
            print(f"  ✅ Найден тип осадков: {prec_name}")
        
        print(f"📊 Всего найдено типов осадков: {len(precipitations)}")
        return precipitations
        
    except Exception as e:
        print(f"❌ Ошибка в get_all_precipitation: {e}")
        return []

def get_all_purposes():
    """Получить все цели выхода (включая подклассы)"""
    print("\n🔍 ПОИСК ЦЕЛЕЙ ВЫХОДА...")
    
    query = """
    PREFIX cl: <http://www.semanticweb.org/user1/ontologies/2025/8/clothing#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?purpose
    WHERE {
        ?purpose a ?type .
        ?type rdfs:subClassOf* cl:ЦельВыхода .
    }
    ORDER BY ?purpose
    """
    
    try:
        qres = graph.query(query)
        purposes = []
        
        for row in qres:
            purpose_name = str(row["purpose"]).split("#")[-1] if "#" in str(row["purpose"]) else str(row["purpose"]).split("/")[-1]
            purposes.append({
                "name": purpose_name
            })
            print(f"  ✅ Найдена цель: {purpose_name}")
        
        print(f"📊 Всего найдено целей: {len(purposes)}")
        return purposes
        
    except Exception as e:
        print(f"❌ Ошибка в get_all_purposes: {e}")
        import traceback
        traceback.print_exc()
        return []

# Определить категорию одежды на основе её типа
def get_clothing_category(clothing_type):
    """Определить категорию одежды на основе её типа"""
    type_lower = clothing_type.lower()
    
    # ВерхняяОдежда
    if any(t in type_lower for t in ['куртка', 'пальто', 'ветровка']):
        return 'ВерхняяОдежда'
    
    # ГоловныеУборы
    if any(t in type_lower for t in ['шапка', 'шляпа']):
        return 'ГоловныеУборы'
    
    # Верх (ЛегкаяОдежда)
    if any(t in type_lower for t in ['футболка', 'рубашка', 'толстовка', 'топ', 'лонгслив', 'свитер']):
        return 'Верх'
    
    # Низ (ЛегкаяОдежда)
    if any(t in type_lower for t in ['брюки', 'джинсы', 'шорты', 'юбка']):
        return 'Низ'
    
    # Цельный комплект
    if any(t in type_lower for t in ['комбинезон', 'костюм', 'платье']):
        return 'ЦельныйКомплект'
    
    # Обувь
    if any(t in type_lower for t in ['босоножки', 'кроссовки', 'сапоги', 'туфли']):
        return 'Обувь'
    
    return 'Другое'

# Найти подходящую одежду по критериям
def find_suitable_clothing(season=None, precipitation=None, purpose=None):
    """Найти подходящую одежду по критериям"""
    print(f"\n🔍 ПОИСК ПОДХОДЯЩЕЙ ОДЕЖДЫ: сезон={season}, осадки={precipitation}, цель={purpose}...")
    
    # Формируем фильтры для запроса
    filters = []
    if season:
        filters.append(f"?season = cl:{season}")
    if precipitation:
        filters.append(f"?precipitation = cl:{precipitation}")
    if purpose:
        filters.append(f"?purpose = cl:{purpose}")
    
    filter_clause = "FILTER(" + " && ".join(filters) + ")" if filters else ""
    
    query = f"""
        PREFIX cl: <http://www.semanticweb.org/user1/ontologies/2025/8/clothing#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT 
            ?name 
            ?brand
            (SAMPLE(?item) AS ?item)
            (SAMPLE(?season) AS ?season)
            (SAMPLE(?precipitation) AS ?precipitation)
            (SAMPLE(?purpose) AS ?purpose)
            (SAMPLE(?type) AS ?type)
        WHERE {{
            ?item cl:Название ?name ;
                cl:Бренд ?brand ;
                cl:подходитДляСезона ?season ;
                cl:подходитДляОсадков ?precipitation ;
                cl:подходитДляЦели ?purpose ;
                a ?type .
                
            ?type rdfs:subClassOf* cl:ЭлементОдежды .
            {filter_clause}
        }}
        GROUP BY ?name ?brand
        ORDER BY ?name
    """
    
    try:
        qres = graph.query(query)
        items = []
        
        for row in qres:
            season_name = str(row["season"]).split("#")[-1] if "#" in str(row["season"]) else str(row["season"]).split("/")[-1]
            prec_name = str(row["precipitation"]).split("#")[-1] if "#" in str(row["precipitation"]) else str(row["precipitation"]).split("/")[-1]
            purpose_name = str(row["purpose"]).split("#")[-1] if "#" in str(row["purpose"]) else str(row["purpose"]).split("/")[-1]
            type_name = str(row["type"]).split("#")[-1] if "#" in str(row["type"]) else str(row["type"]).split("/")[-1]
            category = get_clothing_category(type_name)
            
            items.append({
                "name": str(row["name"]),
                "brand": str(row["brand"]),
                "season": season_name,
                "precipitation": prec_name,
                "purpose": purpose_name,
                "type": type_name,
                "category": category
            })
            print(f"  ✅ Подходит: {row['name']} ({row['brand']}) - {category}")
        
        print(f"📊 Всего найдено подходящих элементов: {len(items)}")
        return items
        
    except Exception as e:
        print(f"❌ Ошибка в find_suitable_clothing: {e}")
        import traceback
        traceback.print_exc()
        return []

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clothing', methods=['POST'])
def display_clothing():
    items = get_all_clothing_items()
    return render_template('clothing.html', items=items)

@app.route('/seasons', methods=['POST'])
def display_seasons():
    seasons = get_all_seasons()
    return render_template('seasons.html', seasons=seasons)

@app.route('/precipitation', methods=['POST'])
def display_precipitation():
    precipitations = get_all_precipitation()
    return render_template('precipitation.html', precipitations=precipitations)

@app.route('/purposes', methods=['POST'])
def display_purposes():
    purposes = get_all_purposes()
    return render_template('purposes.html', purposes=purposes)


@app.route('/suitable', methods=['GET', 'POST'])
def display_suitable():
    if request.method == 'POST':
        season = request.form.get('season', '').strip()
        precipitation = request.form.get('precipitation', '').strip()
        purpose = request.form.get('purpose', '').strip()
        
        # Получаем списки для формы
        seasons = get_all_seasons()
        precipitations = get_all_precipitation()
        purposes = get_all_purposes()
        
        # Ищем подходящую одежду
        items = find_suitable_clothing(
            season=season if season else None,
            precipitation=precipitation if precipitation else None,
            purpose=purpose if purpose else None
        )
        
        # Группируем по категориям
        grouped_items = {
            'ВерхняяОдежда': [item for item in items if item.get('category') == 'ВерхняяОдежда'],
            'ГоловныеУборы': [item for item in items if item.get('category') == 'ГоловныеУборы'],
            'Верх': [item for item in items if item.get('category') == 'Верх'],
            'Низ': [item for item in items if item.get('category') == 'Низ'],
            'ЦельныйКомплект': [item for item in items if item.get('category') == 'ЦельныйКомплект'],
            'Обувь': [item for item in items if item.get('category') == 'Обувь']
        }
        
        return render_template('suitable.html', 
                             items=items, 
                             grouped_items=grouped_items,
                             seasons=seasons, 
                             precipitations=precipitations, 
                             purposes=purposes,
                             selected_season=season,
                             selected_precipitation=precipitation,
                             selected_purpose=purpose)
    else:
        seasons = get_all_seasons()
        precipitations = get_all_precipitation()
        purposes = get_all_purposes()
        return render_template('suitable.html', 
                             items=[], 
                             grouped_items={
                                 'ВерхняяОдежда': [],
                                 'ГоловныеУборы': [],
                                 'Верх': [],
                                 'Низ': [],
                                 'ЦельныйКомплект': [],
                                 'Обувь': []
                             },
                             seasons=seasons, 
                             precipitations=precipitations, 
                             purposes=purposes)

if __name__ == '__main__':
    app.run(debug=True)

