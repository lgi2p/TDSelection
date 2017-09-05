

def read_adapt_result_file_k_1(trad_base_path_, cont_theta_):
	results_dict_ic_trust = dict()
	results_dict_trust_ic = dict()
	f_in = open(trad_base_path_)
	for line in f_in:
		line = line.strip().split("\t")
		dataset_type = line[2]
		dataset_id = line[1]
		if dataset_type not in results_dict_ic_trust:
			results_dict_ic_trust[dataset_type] = dict()
		if dataset_type not in results_dict_trust_ic:
			results_dict_trust_ic[dataset_type] = dict()

		line[3] = line[3][2:-2].split("]], [[") #for obtaining the result at different level of theta - threshold

		result_at_k = line[3][cont_theta_] + "]" # theta = 0 and the different performance for different k
		result_at_k = result_at_k.split("], [")[0] + "]"  #theta = 0 and k = 1
		if len(result_at_k.split(', ')) == 1:
			app = int(result_at_k[1:-1])
			result_at_k = list()
			result_at_k.append(app)
			result_at_k.append(0)
			result_at_k.append(0)
			tot = 10000
		else:
			result_at_k = result_at_k.replace("]", "").replace("[", "").split(', ')
			for pos in range (0, len(result_at_k)):
				result_at_k[pos] = int(result_at_k[pos] )
			tot = sum(result_at_k)
		result_at_k[:] = [x / tot for x in result_at_k]
		results_dict_ic_trust[dataset_type][dataset_id] = result_at_k

		line[4] = line[4][2:-2].split("]], [[")  # for obtaining the result at different level of theta - threshold

		result_at_k = line[4][cont_theta_] + "]"  # theta = 0 and the different performance for different k
		result_at_k = result_at_k.split("], [")[0]+ "]"  # theta = 0 and k = 1
		if len(result_at_k.split(', ')) == 1:
			app = int(result_at_k[1:-1])
			result_at_k = list()
			result_at_k.append(app)
			result_at_k.append(0)
			result_at_k.append(0)
			tot = 10000
		else:
			result_at_k = result_at_k.replace("]", "").replace("[", "").split(', ')
			for pos in range(0, len(result_at_k)):
				result_at_k[pos] = int(result_at_k[pos])
			tot = sum(result_at_k)
		result_at_k[:] = [x / tot for x in result_at_k]
		results_dict_trust_ic[dataset_type][dataset_id] = result_at_k

	return [results_dict_ic_trust, results_dict_trust_ic]


def read_trad_result_file_k_1(trad_base_path_):
	results_dict = dict()
	f_in = open(trad_base_path_)
	for line in f_in:
		line = line.strip().split("\t")
		dataset_type = line[2]
		dataset_id = line[1]
		if dataset_type not in results_dict:
			results_dict[dataset_type] = dict()
		line[4] = line[4][1:-1]
		result_at_k = line[4].split(', ')[0] #pos 0 is for number of returned values equals to 1
		if len(result_at_k.split(', ')) == 1:
			app = int(result_at_k[1:-1])
			result_at_k = list()
			result_at_k.append(app)
			result_at_k.append(0)
			result_at_k.append(0)
			tot = 10000
		else:
			result_at_k = result_at_k[1:-1].split(', ')
			for item in result_at_k:
				item = int(item)
			tot = sum(result_at_k)
		result_at_k[:] = [x / tot for x in result_at_k]
		results_dict[dataset_type][dataset_id] = result_at_k
	return results_dict


def compute_average(results, dataset_types_):
	average_for_type = dict()
	for type_ in dataset_types_:
		if type_ in results:
			sum_ = [0, 0, 0]
			for dataset_id in results[type_]:
				performance_dataset = results[type_][dataset_id]
				for pos in range(0, len(sum_)):
					sum_[pos] += performance_dataset[pos]

			average_for_type[type_] = [x / len(results[type_]) for x in sum_]

	return average_for_type


if __name__ == '__main__':
	norm_flag = True
	predicates = ["BP", "birthPlace", "genre", "CC", "MF"]
	name_models = ["Adapt10", "Adapt11", "Adapt14", "Adapt15"]
	dataset_types = ["EXP", "LOW_E", "UNI"]
	precision_k = dict()  # precision_k is a dict : <[model_name], subdict_at_k is a dict <dataset_kind, [list with k precision level]
	theta_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
	for predicate in predicates:
		print(predicate)
		base_dir = "D:\\MyDownload\\results-Jan2017\\conf_evaluations_threshold_norm\\" + str(predicate)
		trad_base_path = str(base_dir) + "\\trad_perf_res_" + str(predicate) + ".csv"
		#at the moment it contains only the # of expected value (no general, no error number)
		trad_results = read_trad_result_file_k_1(trad_base_path)
		trad_results = compute_average(trad_results, dataset_types)
		for type_ in dataset_types:
			print("----" + str(type_) +"\t" + str(trad_results[type_]))

		print("ADAPT 14")
		for cont_theta in range(0, len(theta_list)):
			#print("THETA " + str(theta_list[cont_theta]))
			delta_0_path = str(base_dir) + "\\delta_0_ordered\\ic_source_average\\theta_0\\adapt_perf_res_" + str(predicate) + "_norm.csv"
			delta_0_results = read_adapt_result_file_k_1(delta_0_path, cont_theta)
			adapt_14 = delta_0_results[0]
			adapt_14 = compute_average(adapt_14, dataset_types)

			str_out = ""
			for type_ in dataset_types:
				str_out += str(adapt_14[type_]) + "\t"
				#print("----" + str(type_) +"\t" + str(adapt_14[type_]))
			print(str_out)

			adapt_10 = delta_0_results[1]
			adapt_10 = compute_average(adapt_10, dataset_types)
			if False:
				print("ADAPT 10")
				for type_ in dataset_types:
					print("----" + str(type_) +"\t" + str(adapt_10[type_]))

			delta_1_path = str(base_dir) + "\\delta_1_not_ordered\\ic_source_average\\theta_0\\adapt_perf_res_" + str(predicate) + "_norm.csv"

			delta_1_results = read_adapt_result_file_k_1(delta_1_path, cont_theta)
			adapt_15 = delta_1_results[0]
			adapt_15 = compute_average(adapt_15, dataset_types)
			if False:
				print("ADAPT 15")
				for type_ in dataset_types:
					print("----" + str(type_) +"\t" + str(adapt_15[type_]))



			###
		print("ADAPT 11")
		for cont_theta in range(0, len(theta_list)):
			#print("THETA " + str(theta_list[cont_theta]))
			delta_0_path = str(base_dir) + "\\delta_0_ordered\\ic_source_average\\theta_0\\adapt_perf_res_" + str(predicate) + "_norm.csv"
			delta_0_results = read_adapt_result_file_k_1(delta_0_path, cont_theta)

			adapt_10 = delta_0_results[1]
			adapt_10 = compute_average(adapt_10, dataset_types)
			if False:
				print("ADAPT 10")
				for type_ in dataset_types:
					print("----" + str(type_) +"\t" + str(adapt_10[type_]))

			delta_1_path = str(base_dir) + "\\delta_1_not_ordered\\ic_source_average\\theta_0\\adapt_perf_res_" + str(predicate) + "_norm.csv"

			delta_1_results = read_adapt_result_file_k_1(delta_1_path, cont_theta)
			adapt_15 = delta_1_results[0]
			adapt_15 = compute_average(adapt_15, dataset_types)
			if False:
				print("ADAPT 15")
				for type_ in dataset_types:
					print("----" + str(type_) +"\t" + str(adapt_15[type_]))

			adapt_11 = delta_1_results[1]
			adapt_11 = compute_average(adapt_11, dataset_types)
			#print("ADAPT 11")
			str_out = ""
			for type_ in dataset_types:
				str_out += str(adapt_11[type_]) + "\t"
				#print("----" + str(type_) +"\t" + str(adapt_11[type_]))
			print(str_out)
		exit()