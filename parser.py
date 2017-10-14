# ! #!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

base_url = "http://www.i-oyacomi.net/prepass/"
output_json_file = open(sys.argv[0], 'w')
output_json_file.write(json.dumps(load_prepass_data(base_url), ensure_ascii=False))
output_json_file.close()
