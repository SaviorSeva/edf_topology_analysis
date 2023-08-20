import json

with open('stats-cpl-k/stats-cpl-k.log') as stats_cpl_k_file:
    for stats_cpl_k_line in stats_cpl_k_file:

        data = json.loads(stats_cpl_k_line)

        print(data['MacEtendue'])
