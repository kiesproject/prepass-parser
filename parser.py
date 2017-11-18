# ! #!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
from parse_csv import load_prepass_data

base_url = "http://www.i-oyacomi.net/prepass/"
output_json_file = open(sys.argv[1], 'w')
output_json_file.write(json.dumps(load_prepass_data(base_url), ensure_ascii=False, indent=2))
output_json_file.close()
