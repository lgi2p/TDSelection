import sys
import os
import copy
import datetime
from TDO.utils_tdo import utils_normalize_conf
from TDO.utils_tdo import utils_predicate
from TDO.experiments.model import preprocessing_sums_model
from TDO.utils_tdo import utils_dataset
from TDO.utils_tdo import utils_writing_results
from TDO.experiments.truth_selection import selection_algorithm
from TDO.experiments.model import sums_model

def read_file_results(path_file, predicate_):
	dict_solution_TRUST = dict()
	dict_solution_IC = dict()

	f_in = open(path_file, 'r')
	for line in f_in:
		if predicate_ == 'genre':
			line = bytes(line, 'utf-8')
			#print(dataitem)
			line = str(line, 'unicode-escape')
			#print(dataitem)
		line = line.strip().split('\t')
		if len(line) != 4 and len(line) != 2:
			print("error ici")
			print(line)
			exit()
		threshold = float(line[0])
		dataitem = line[1]
		if len(line) == 2:
			sol_IC = "None"
			sol_TRUST = "None"
		else:
			sol_IC = line[2].split(" ")
			sol_TRUST = line[3].split(" ")
		if threshold not in dict_solution_IC:
			dict_solution_IC[threshold] = dict()
		dict_solution_IC[threshold][dataitem] = sol_IC
		if threshold not in dict_solution_TRUST:
			dict_solution_TRUST[threshold] = dict()
		dict_solution_TRUST[threshold][dataitem] = sol_TRUST

	return [dict_solution_IC, dict_solution_TRUST]


if __name__ == '__main__':
	try:
		#analysis results with K = 1
		threshold_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
		predicate = "BP"#sys.argv[1]
		dataset_kind_list = ["EXP", "LOW_E", "UNI"]
		# path_results = "C:\\results_final\\" + str(predicate) + "\\"+ str(dataset_kind)#sys.argv[2]
		prefix_str_list = ["solutions_all_children_", "solutions_best_children"]


		prefix_str = "solutions_all_children_"
		#prefix_str = "solutions_best_children"

		base_dir = "../required_files/"

		if not (utils_predicate.set_predicate(predicate)):
			print("Error in setting predicate name")
			exit()

		predicate_info = utils_predicate.loading_predicate_info(base_dir, predicate)
		ground = predicate_info[7]
		ancestors = predicate_info[2]

		for prefix_str in prefix_str_list:
			for dataset_kind in dataset_kind_list:
				path_results = "C:\\results_final\\" + str(predicate) + "\\" + str(dataset_kind)  # sys.argv[2]
				performances_tot_ic = dict()
				performances_tot_trust = dict()

				for root, dirs, files in os.walk(path_results):
					for file_to_read in files:
						if file_to_read.startswith(prefix_str):
							id_dataset = file_to_read.replace(prefix_str, "")
							id_dataset = id_dataset.replace(".csv", "")
							solutions_dict = read_file_results(str(root)+"\\"+ str(file_to_read), predicate)
							dict_solution_IC_final = solutions_dict[0]
							dict_solution_TRUST_final = solutions_dict[1]
							if id_dataset not in performances_tot_ic: performances_tot_ic[id_dataset] = dict()
							if id_dataset not in performances_tot_trust: performances_tot_trust[id_dataset] = dict()
							k = 1
							#print("ALL CHILDREN - IC")
							for threshold in threshold_list:

								cont_d = 0
								n_expected = 0
								n_general = 0
								n_error = 0
								for d in dict_solution_IC_final[threshold]:
									cont_d +=1
									returned_sol_list = dict_solution_IC_final[threshold][d]
									returned_sol = returned_sol_list[k-1]
									if returned_sol == "None":
										n_error += 1
										continue
									expected_sol = ground[d]

									if expected_sol in returned_sol_list:
										n_expected += 1
									else:
										if returned_sol in ancestors[expected_sol]:
											n_general += 1
										else:
											n_error += 1
								#print(cont_d)
								if (cont_d != n_error+n_general+n_expected):
									print("ERRORE")
									exit()
								performances_tot_ic[id_dataset][threshold] = [n_expected/cont_d, n_general/cont_d, n_error/cont_d]
								#print(str(threshold) + "\t" + str(n_expected) +"\t" + str(n_general) + "\t" + str(n_error))

							#print("ALL CHILDREN - TRUST ")
							for threshold in threshold_list:

								cont_d = 0
								n_expected = 0
								n_general = 0
								n_error = 0
								for d in dict_solution_TRUST_final[threshold]:
									cont_d += 1
									returned_sol_list = dict_solution_TRUST_final[threshold][d]
									returned_sol = returned_sol_list[k - 1]
									expected_sol = ground[d]

									if expected_sol in returned_sol_list:
										n_expected += 1
									else:
										if returned_sol in ancestors[expected_sol]:
											n_general += 1
										else:
											n_error += 1
								#print(cont_d)
								if (cont_d != n_error+n_general+n_expected):
									print("ERRORE")
									exit()
								performances_tot_trust[id_dataset][threshold] = [n_expected / cont_d, n_general / cont_d,
								                                           n_error / cont_d]
								#print(str(threshold) + "\t" + str(n_expected) + "\t" + str(n_general) + "\t" + str(n_error))
						#print("")

				#compute average for each threshold for such dataset type(EXP) and predicate (Es.CC)
				#first ranking = IC
				if prefix_str == "solutions_all_children_":
					model_name = "TSaC_ic"
				else:
					model_name = "TSbC_ic"
				for threshold in threshold_list:
					n_exp_average = 0
					n_gen_average = 0
					n_err_average = 0
					for id_dataset in performances_tot_ic:
						perf = performances_tot_ic[id_dataset][threshold]
						n_exp_average += perf[0]
						n_gen_average += perf[1]
						n_err_average += perf[2]
					#print(len(performances_tot_ic))
					n_exp_average /= len(performances_tot_ic)
					n_gen_average /= len(performances_tot_ic)
					n_err_average /= len(performances_tot_ic)
					print(str(model_name) + '\t' + str(predicate) + '\t' + str(dataset_kind) +'\t' + str(threshold) + '\t'+ str(n_exp_average)+ '\t'+ str(n_gen_average)+ '\t'+ str(n_err_average))

				# first ranking = TRUST
				if prefix_str == "solutions_all_children_":
					model_name = "TSaC_trust"
				else:
					model_name = "TSbC_trust"
				for threshold in threshold_list:
					n_exp_average = 0
					n_gen_average = 0
					n_err_average = 0
					for id_dataset in performances_tot_trust:
						perf = performances_tot_trust[id_dataset][threshold]
						n_exp_average += perf[0]
						n_gen_average += perf[1]
						n_err_average += perf[2]
					n_exp_average /= len(performances_tot_trust)
					n_gen_average /= len(performances_tot_trust)
					n_err_average /= len(performances_tot_trust)
					print(str(model_name) + '\t' + str(predicate) + '\t' + str(dataset_kind) + '\t' + str(threshold) + '\t' + str(
						n_exp_average) + '\t' + str(n_gen_average) + '\t' + str(n_err_average))










	except:
		print("Unexpected error:", sys.exc_info()[0])
