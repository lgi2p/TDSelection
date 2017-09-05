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

	f_in  = open(path_file, 'r')
	for line in f_in:
		if predicate_ == 'genre':
			line = bytes(line, 'utf-8')
			line = str(line, 'unicode-escape')
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

def read_file_results_trad(path_file, predicate_):
	dict_solution = dict()

	f_in = open(path_file, 'r')
	for line in f_in:
		if predicate_ == 'genre':
			line = bytes(line, 'utf-8')
			line = str(line, 'unicode-escape')
		line = line.strip().split('\t')
		if len(line) != 2:
			print("error ici")
			print(line)
			exit()
		dataitem = line[0]
		sol_trad = line[1].split(" ")
		dict_solution[dataitem] = sol_trad


	return dict_solution

if __name__ == '__main__':
	try:
		#analysis results with K = 1
		threshold_list = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
		predicate = "CC"#sys.argv[1]
		dataset_kind_list = ["EXP", "LOW_E", "UNI"]
		#path_results = "C:\\results_final\\" + str(predicate) + "\\"+ str(dataset_kind)#sys.argv[2]

		#prefix_str = "solutions_best_children"
		base_dir = "D:/thesis_code/TDO/required_files/"

		if not (utils_predicate.set_predicate(predicate)):
			print("Error in setting predicate name")
			exit()

		predicate_info = utils_predicate.loading_predicate_info(base_dir, predicate)
		ground = predicate_info[7]
		ancestors = predicate_info[2]

		if False: #analyse file traditional SUMS
			prefix_str_list = ["solutions_trad_Sums_"]
			for prefix_str in prefix_str_list:
				for dataset_kind in dataset_kind_list:
					#path_results = "C:\\results_final_no_desc\\" + str(predicate) + "\\" + str(dataset_kind)  # sys.argv[2]
					path_results = "..\\results_final_trad\\" + str(predicate) + "\\" + str(dataset_kind)  # sys.argv[2]
					performances_tot_trad = dict()

					for root, dirs, files in os.walk(path_results):
						for file_to_read in files:
							if file_to_read.startswith(prefix_str):
								id_dataset = file_to_read.replace(prefix_str, "")
								id_dataset = id_dataset.replace(".csv", "")
								solutions_dict = read_file_results_trad(str(root)+"\\"+ str(file_to_read), predicate)
								if id_dataset not in performances_tot_trad: performances_tot_trad[id_dataset] = dict()

								#print("ALL CHILDREN - IC")

								cont_d = 0
								n_expected = 0
								n_general = 0
								n_error = 0
								precision_at_k = dict()
								recall_at_k = dict()
								for k in range(1, 6):
									precision_at_k[k] = 0
									recall_at_k[k] = 0
								for d in solutions_dict:
									cont_d += 1
									returned_sol_list = solutions_dict[d]
									for k in range(1, 6):
										returned_sol = set(returned_sol_list[0:k])
										expected_sol = set()
										expected_sol.add(ground[d])

										precision = len(returned_sol.intersection(expected_sol)) / len(returned_sol)
										precision_at_k[k] += precision
										recall = len(returned_sol.intersection(expected_sol)) / len(expected_sol)
										recall_at_k[k] += recall

									#print(cont_d)
								for k in range(1, 6):
									precision_at_k[k] /= cont_d
									recall_at_k[k] /= cont_d
								performances_tot_trad[id_dataset] = [precision_at_k, recall_at_k]

					prec_at_k_average = dict()
					rec_at_k_average = dict()
					for k in range(1, 6):
						prec_at_k_average[k] = 0
						rec_at_k_average[k] = 0

					for id_dataset in performances_tot_trad:
						precision_at_k = performances_tot_trad[id_dataset][0]
						recall_at_k = performances_tot_trad[id_dataset][1]

						for k in range(1, 6):
							prec_at_k_average[k] += precision_at_k[k]
							rec_at_k_average[k] += recall_at_k[k]

					for k in range(1, 6):
						prec_at_k_average[k] /= len(performances_tot_trad)
						rec_at_k_average[k] /= len(performances_tot_trad)
					#print('precision\tSums\t' + str(predicate) + '\t' + str(dataset_kind) + '\t' + str(prec_at_k_average[1]) + '\t' + str(prec_at_k_average[2]) + '\t' + str(prec_at_k_average[3]) + '\t' + str(prec_at_k_average[4]) + '\t' + str(prec_at_k_average[5]))
					print("recall\t\tSums\t" + str(predicate) + '\t' + str(dataset_kind) + '\t' + str(rec_at_k_average[1]) + '\t' + str(rec_at_k_average[2]) + '\t' + str(rec_at_k_average[3]) + '\t' + str(rec_at_k_average[4]) + '\t' + str(rec_at_k_average[5]))

			exit()

		prefix_str_list = ["solutions_all_children_", "solutions_best_children"]
		for prefix_str in prefix_str_list:
			for dataset_kind in dataset_kind_list:
				#path_results = "C:\\results_final_no_desc\\" + str(predicate) + "\\" + str(dataset_kind)  # sys.argv[2]
				path_results = "..\\results_final\\" + str(predicate) + "\\" + str(dataset_kind)  # sys.argv[2]
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
								precision_at_k = dict()
								recall_at_k = dict()
								for k in range(1, 6):
									precision_at_k[k] = 0
									recall_at_k[k] = 0
								for d in dict_solution_IC_final[threshold]:
									cont_d += 1
									returned_sol_list = dict_solution_IC_final[threshold][d]
									for k in range(1, 6):
										returned_sol = set(returned_sol_list[0:k])
										expected_sol = set()
										expected_sol.add(ground[d])

										precision = len(returned_sol.intersection(expected_sol)) / len(returned_sol)
										precision_at_k[k] += precision
										recall = len(returned_sol.intersection(expected_sol)) / len(expected_sol)
										recall_at_k[k] += recall

								#print(cont_d)
								for k in range(1, 6):
									precision_at_k[k] /= cont_d
									recall_at_k[k] /= cont_d
								performances_tot_ic[id_dataset][threshold] = [precision_at_k, recall_at_k]
								#print(str(threshold) + "\t" + str(n_expected) +"\t" + str(n_general) + "\t" + str(n_error))

							#print("ALL CHILDREN - TRUST ")
							for threshold in threshold_list:

								cont_d = 0
								n_expected = 0
								n_general = 0
								n_error = 0
								precision_at_k = dict()
								recall_at_k = dict()
								for k in range(1, 6):
									precision_at_k[k] = 0
									recall_at_k[k] = 0
								for d in dict_solution_TRUST_final[threshold]:
									cont_d += 1
									returned_sol_list = dict_solution_TRUST_final[threshold][d]
									for k in range(1, 6):
										returned_sol = set(returned_sol_list[0:k])
										expected_sol = set()
										expected_sol.add(ground[d])

										precision = len(returned_sol.intersection(expected_sol)) / k
										#if k==5:
										#	print(str(precision) +"\t" + str(len(returned_sol.intersection(expected_sol)) ) + "\t" + str(k))
										precision_at_k[k] += precision
										recall = len(returned_sol.intersection(expected_sol)) / len(expected_sol)
										recall_at_k[k] += recall
								#print("OKOK")
								#print(cont_d)
								for k in range(1, 6):
									precision_at_k[k] /= cont_d
									recall_at_k[k] /= cont_d
								performances_tot_trust[id_dataset][threshold] = [precision_at_k, recall_at_k]
								#print(str(threshold) + "\t" + str(n_expected) + "\t" + str(n_general) + "\t" + str(n_error))
						#print("")


				#compute average for each threshold for such dataset type(EXP) and predicate (Es.CC)
				#first ranking = IC
				if prefix_str == "solutions_all_children_":
					model_name = "TSaC_ic"
				else:
					model_name = "TSbC_ic"
				for threshold in threshold_list:
					prec_at_k_average = dict()
					rec_at_k_average = dict()
					for k in range(1, 6):
						prec_at_k_average[k] = 0
						rec_at_k_average[k] = 0

					for id_dataset in performances_tot_ic:
						precision_at_k = performances_tot_ic[id_dataset][threshold][0]
						recall_at_k = performances_tot_ic[id_dataset][threshold][1]

						for k in range(1, 6):
							prec_at_k_average[k] += precision_at_k[k]
							rec_at_k_average[k] += recall_at_k[k]

					for k in range(1, 6):
						prec_at_k_average[k] /= len(performances_tot_trust)
						rec_at_k_average[k] /= len(performances_tot_trust)
					print("precision\t" +str(model_name) + '\t' + str(predicate) + '\t' + str(dataset_kind) +'\t' + str(threshold) + '\t'+ str(prec_at_k_average[1])+ '\t'+ str(prec_at_k_average[2])+ '\t'+ str(prec_at_k_average[3])+ '\t'+ str(prec_at_k_average[4])+ '\t'+ str(prec_at_k_average[5]))
					print("recall\t" +str(model_name) + '\t' + str(predicate) + '\t' + str(dataset_kind) + '\t' + str(threshold) + '\t' + str(
						rec_at_k_average[1]) + '\t' + str(rec_at_k_average[2]) + '\t' + str(rec_at_k_average[3]) + '\t' + str(
						rec_at_k_average[4]) + '\t' + str(rec_at_k_average[5]))

				# first ranking = TRUST
				if prefix_str == "solutions_all_children_":
					model_name = "TSaC_trust"
				else:
					model_name = "TSbC_trust"
				for threshold in threshold_list:
					prec_at_k_average = dict()
					rec_at_k_average = dict()
					for k in range(1, 6):
						prec_at_k_average[k] = 0
						rec_at_k_average[k] = 0

					for id_dataset in performances_tot_ic:
						precision_at_k = performances_tot_trust[id_dataset][threshold][0]
						recall_at_k = performances_tot_trust[id_dataset][threshold][1]

						for k in range(1, 6):
							prec_at_k_average[k] += precision_at_k[k]
							rec_at_k_average[k] += recall_at_k[k]

					for k in range(1, 6):
						prec_at_k_average[k] /= len(performances_tot_trust)
						rec_at_k_average[k] /= len(performances_tot_trust)
					print("precision\t" + str(model_name) + '\t' + str(predicate) + '\t' + str(dataset_kind) +'\t' + str(threshold) + '\t'+ str(prec_at_k_average[1])+ '\t'+ str(prec_at_k_average[2])+ '\t'+ str(prec_at_k_average[3])+ '\t'+ str(prec_at_k_average[4])+ '\t'+ str(prec_at_k_average[5]))
					print("recall\t" + str(model_name) + '\t' + str(predicate) + '\t' + str(dataset_kind) + '\t' + str(threshold) + '\t' + str(
						rec_at_k_average[1]) + '\t' + str(rec_at_k_average[2]) + '\t' + str(rec_at_k_average[3]) + '\t' + str(
						rec_at_k_average[4]) + '\t' + str(rec_at_k_average[5]))

	except:
		print("Unexpected error:", sys.exc_info()[0])
