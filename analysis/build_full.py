# -*- coding: utf-8 -*-
# Publishes sales_explorer.html + index.html from app2_template.html.
#
# HISTORY: this used to apply ~14 numbered string-patch steps to an upstream
# template (see build_full.py.legacy), then later spliced a build-time JSON
# data blob into a placeholder token in the template. Both are gone. The
# template is now fully self-sufficient — data loads live at page-load time
# from jps_billing_components/jps_kam/jps_industries via bootstrapExplorerData()
# in the template's own <script>. EDIT app2_template.html DIRECTLY; this
# script just copies it to the two published filenames.
import io

t = io.open('app2_template.html', encoding='utf-8').read()

io.open('sales_explorer.html', 'w', encoding='utf-8').write(t)
io.open('index.html', 'w', encoding='utf-8').write(t)
print('built sales_explorer.html', len(t.encode("utf-8")), 'bytes')
