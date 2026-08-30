from app import create_app, db
from app.models import SearchRetrieval

app = create_app('development')
with app.app_context():
    searches = SearchRetrieval.query.all()
    print(f'Total searches in database: {len(searches)}')
    
    if searches:
        for i, s in enumerate(searches[:5], 1):
            print(f'Search {i}: Event {s.event_id}, Model {s.model_type}, {s.num_matches} matches, {s.processing_time_ms:.1f}ms')
    else:
        print('No searches found in database')
