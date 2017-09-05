import math
from TDO.utils_tdo import utils_predicate


def compute_seco_ic(inclusive_desc):
	quantity_set = set()
	seco_dict = dict()

	for value in inclusive_desc:

		ic_meas = 1 - (math.log10(len(inclusive_desc[value])) / math.log10(len(inclusive_desc)))
		seco_dict[value] = ic_meas
		quantity_set.add(ic_meas)
		if ic_meas < 0:
			print(value)

	print(max(quantity_set))
	print(min(quantity_set))
	return seco_dict


predicate = 'birthPlace'

base_dir = "../required_files/"
if predicate == 'genre':
	base_dir = base_dir + "genre/"
	graph_file = base_dir + 'ancestors_heuristic_genre_base.csv'
	graph_file_reduced = base_dir + 'ancestors_heuristic_genre_base_tr.csv'
	children_file = base_dir + "children_genre_base.csv"
	path_ground_file = base_dir + 'sample_genre_base_3.csv'
	descendants_file = base_dir + 'descendants_genre_base.csv'
else:  # the predicate is 'birthPlace'
	if predicate == 'birthPlace':
		base_dir = base_dir + "birthPlace/"
		graph_file = base_dir + 'ancestors_heuristic.csv'
		graph_file_reduced = base_dir + 'ancestors_heuristic_tr.csv'
		children_file = base_dir + "children.csv"
		path_ground_file = base_dir + 'sample_ground_grouped.csv'
		descendants_file = base_dir + 'specific_value_new.csv'
		ic_old_path = base_dir + 'seco_IC_birthPlace.csv'
	else:  # the predicate is CC
		base_dir = base_dir + predicate + "/"
		graph_file = base_dir + 'output_' + predicate + '_ancestors.tsv'
		graph_file_reduced = base_dir + 'output_' + predicate + '_ancestors_tr.tsv'
		children_file = base_dir + 'output_' + predicate + '_children.tsv'
		path_ground_file = base_dir + 'sample_ground_' + predicate + '.csv'
		descendants_file = base_dir + 'output_' + predicate + '_descendants.tsv'

# descendants_file ='specific_value_2ev_birthPlace.csv'

if predicate == 'genre' or predicate == 'birthPlace':
	print(descendants_file)
	descendants = utils_predicate.loading_descendants_dbpedia(descendants_file)
	print("number of descendants " + str(len(descendants)))
else:
	descendants = utils_predicate.loading_descendents_or_ancestors_go(descendants_file)[0]
	print("number of descendants " + str(len(descendants)))

seco_dict = compute_seco_ic(descendants)

seco_old = utils_predicate.load_ic(ic_old_path)

print("print different ic")
for item in seco_dict:
	if item in seco_old:
		if abs(seco_dict[item] - seco_old[item]) > 0.000001:
			print(str(item) + '\t' + str(seco_dict[item]) + '\t' + str(seco_old[item]))

print("print not in ic dict old, but in new")
for item in seco_dict:
	if item not in seco_old:
		print(item)
exit()
# write file seco's IC
f = open("seco_IC_" + str(predicate) + ".csv", "w")
for item in seco_dict:
	f.write(str(item) + '\t' + str(seco_dict[item]) + '\n')
f.close()
