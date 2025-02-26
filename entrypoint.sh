#!/bin/bash
set -e

# Activate the virtualenv
source ./env/bin/activate

# Run database migrations
python manage.py migrate --noinput

# Create default superuser if not exists
echo "from django.contrib.auth import get_user_model; User = get_user_model(); x = not User.objects.filter(username='root').exists(); User.objects.create_superuser('root','root@redteam-test.com','redteamroxs') if x else None" | python manage.py shell

# Add the risk levels
python manage.py shell -c "import json; from reportgen.models import RiskLevel; [RiskLevel.objects.get_or_create(risk_level_name=item['risk_level_name'], risk_matrix_row=int(item['risk_matrix_row']), risk_matrix_col=int(item['risk_matrix_col'])) for item in json.load(open('default_data_jsons/risk_levels.json'))]"

# Add score override defaults
python manage.py shell -c "import json; from reportgen.models import ScoreOverride; [ScoreOverride.objects.get_or_create(score_override_name=item['score_override_name'], score_override_value=float(item['score_override_value'])) for item in json.load(open('default_data_jsons/score_overrides.json'))]"

# Add solution override defaults
python manage.py shell -c "import json; from reportgen.models import SolutionOverride; [SolutionOverride.objects.get_or_create(vulnerability_title=item['vulnerability_title'], solution_body=item['solution_body'], see_also=item.get('see_also', '')) for item in json.load(open('default_data_jsons/solution_overrides.json'))]"

# Add TestFrom defaults
python manage.py shell -c "import json; from reportgen.models import TestFrom; [TestFrom.objects.get_or_create(test_from_name=item['test_from_name'], test_from_value=item['test_from_value']) for item in json.load(open('default_data_jsons/test_from.json'))]"

# Add TestType defaults
python manage.py shell -c "import json; from reportgen.models import TestType; [TestType.objects.get_or_create(test_name=item['test_name'], test_value=item['test_value']) for item in json.load(open('default_data_jsons/test_type.json'))]"

# Add Strength defaults
python manage.py shell -c "import json; from reportgen.models import Strength; [Strength.objects.get_or_create(strength_subtle=item['strength_subtle']) for item in json.load(open('default_data_jsons/strength.json'))]"

# Add Improvements
python manage.py shell -c "import json; from reportgen.models import Improvement; [Improvement.objects.get_or_create(improvement_subtle=item['improvement_subtle']) for item in json.load(open('default_data_jsons/improvement.json'))]"

# Execute Gunicorn
gunicorn mojo.wsgi:application --bind 0.0.0.0:8000 --workers 3
