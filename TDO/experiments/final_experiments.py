import shutil
import sys
import os
import copy
import gc
from TDO.utils_tdo import utils_normalize_conf
from TDO.utils_tdo import utils_predicate
from TDO.experiments.model import preprocessing_sums_model
from TDO.utils_tdo import utils_dataset
from TDO.utils_tdo import utils_writing_results
from TDO.experiments.truth_selection import selection_algorithm
from TDO.experiments.model import sums_model

if __name__ == '__main__':
	try:
		####initiliazation parameters!!! predicate and its information
		#Exemple of paramters : "predicate  [threshold_list] k_max Sums_flag TSbC_flag TSaC_flag [dataset_already evaluated]"
		# birthPlace [0.0,0.1,0.2,0.3,0.4,0.50] 5 True True True
		cwd_here = os.getcwd()
		base_directory = cwd_here.replace("\\experiments", "")
		#print(base_directory)
		predicate = sys.argv[1]
		threshold_list = (sys.argv[2][1:-1]).split(",")
		index_ = 0
		for threshold in threshold_list:
			threshold = float(threshold)
			threshold_list[index_] = threshold
			index_ += 1

		k_expected = int(sys.argv[3])
		if sys.argv[4] == 'True':
			Sums_flag = True
		else:
			if sys.argv[4] == 'False':
				Sums_flag = False

		if sys.argv[5] == 'True':
			TSbC_flag = True
		else:
			if sys.argv[5] == 'False':
				TSbC_flag = False

		if sys.argv[6] == 'True':
			TSaC_flag = True
		else:
			if sys.argv[6] == 'False':
				TSaC_flag = False

		trust_average_normalized = True
		already_processed = list()
		if len(sys.argv) > 7:
			str_list = sys.argv[7]
			str_list = str_list[+1:-1]
			for item in str_list.split(','):
				already_processed.append(item)
		# end initialization parameter from the user

		if not (utils_predicate.set_predicate(predicate)):
			print("Error in setting predicate name")
			exit()

		base_dir = base_directory + "/required_files/"
		#base_dir = "D:\\thesis_code\\TDO\\required_files/"
		predicate_info = utils_predicate.loading_predicate_info(base_dir, predicate)

		#predicate_info[0].clear()
		predicate_info[3].clear()

		g = predicate_info[5]
		ground = predicate_info[7]
		gc.collect()

		####initialization variable of file path
		path_datasets = base_directory+ "\\datasets\\dataset_" + str(predicate)
		#path_datasets = "D:\\thesis_code\\TDO\\datasets\\dataset_" + str(predicate)
		results_folder = base_directory+ "\\results\\" + str(predicate) + "\\"
		if not os.path.exists(results_folder):
			os.makedirs(results_folder)
		solution_folder_trad_base = base_directory+"/results_final_trad/" + str(predicate) + "/"
		solution_folder_adapt_base = base_directory+"/results_final/" + str(predicate) + "/"

		cont_datasets = 0
		# initialization
		model_name = "sums"
		# Constants
		initial_trustworthiness = 0.8
		initial_confidence = 0.5
		max_iteration_number = 20  # 20
		D = list()
		T = list()
		S_set = list()
		fact_and_source_info = list()
		dataitem_values_info = list()
		F_s = dict()
		S_prop = dict()
		S = dict()
		sources_dataItemValues = dict()
		dataitem_ids = dict()

		cont_subfolders = 0
		for folder_type in ["EXP", "LOW_E", "UNI"]:
			root = os.path.join(path_datasets, folder_type)
			dirs = os.listdir(root)
			#if "EXP" in root or "UNI" in root :continue

			for dir_name in dirs:
				print("dir name :" + str(dir_name))
				if dir_name in already_processed:
					cont_datasets += 1
					continue
				dir_name = dir_name.replace("dataset", "")

				n_dataset = dir_name
				if "-" in n_dataset:
					n_dataset = n_dataset.replace("UNI-", "")
					n_dataset = n_dataset.replace("EXP-", "")
					n_dataset = n_dataset.replace("LOW_E-", "")
					n_dataset = n_dataset.replace("-", "")
					n_folder_app = "-" + str(n_dataset[0:2])
					n_dataset = n_dataset[2:]
					n_folder_app = n_folder_app + n_dataset

				else:
					n_dataset = n_dataset.replace("UNI_", "")
					n_dataset = n_dataset.replace("EXP_", "")
					n_dataset = n_dataset.replace("LOW_E_", "")
					if n_dataset.startswith("_"): n_dataset = n_dataset.replace("_", "")
					n_folder_app = "_"
					n_folder_app = n_folder_app + n_dataset

				# claims file path
				if "UNI" in root:
					dataset_kind_ = "UNI"
					subfolder_path = "UNI/dataset" + str(n_folder_app) + "/"
					facts_file = path_datasets + "/UNI/dataset" + str(n_folder_app) + "/facts_" + str(
						n_dataset) + ".csv"
					source_file = path_datasets + "/UNI/dataset" + str(n_folder_app) + "/Output_acc_" + str(
						n_dataset) + ".txt"
					dataitem_index_file = path_datasets + "/UNI/dataset" + str(
						n_folder_app) + "/dataitems_index_" + str(n_dataset) + ".csv"
					confidence_value_computation_info_dir = path_datasets + "/UNI/dataset" + str(
						n_folder_app) + "/confidence_value_computation_info/"

				if "EXP" in root:
					dataset_kind_ = "EXP"
					subfolder_path = "EXP/dataset" + str(n_folder_app) + "/"
					facts_file = path_datasets + "/EXP/dataset" + str(n_folder_app) + "/facts_" + str(
						n_dataset) + ".csv"
					source_file = path_datasets + "/EXP/dataset" + str(n_folder_app) + "/Output_acc_" + str(
						n_dataset) + ".txt"
					dataitem_index_file = path_datasets + "/EXP/dataset" + str(
						n_folder_app) + "/dataitems_index_" + str(n_dataset) + ".csv"
					confidence_value_computation_info_dir = path_datasets + "/EXP/dataset" + str(
						n_folder_app) + "/confidence_value_computation_info/"

				if "LOW_E" in root:
					dataset_kind_ = "LOW_E"
					subfolder_path = "LOW_E/dataset" + str(n_folder_app) + "/"
					facts_file = path_datasets + "/LOW_E/dataset" + str(n_folder_app) + "/facts_" + str(
						n_dataset) + ".csv"
					source_file = path_datasets + "/LOW_E/dataset" + str(n_folder_app) + "/Output_acc_" + str(
						n_dataset) + ".txt"
					dataitem_index_file = path_datasets + "/LOW_E/dataset" + str(
						n_folder_app) + "/dataitems_index_" + str(n_dataset) + ".csv"
					confidence_value_computation_info_dir = path_datasets + "/LOW_E/dataset" + str(
						n_folder_app) + "/confidence_value_computation_info/"

				if not os.path.exists(confidence_value_computation_info_dir): os.makedirs(
					confidence_value_computation_info_dir)

				#output files
				trust_file_base = os.path.join(results_folder, "dataset" + dir_name)
				if not os.path.exists(trust_file_base):
					os.makedirs(trust_file_base)
				if Sums_flag:
					trust_file_trad_for_iter = os.path.join(trust_file_base, "trad_trust_est_at_eac_iter" + str(dir_name) + ".csv")
					trust_file_trad = os.path.join(trust_file_base, "trad_trust_est" + str(dir_name) + ".csv")
					solution_folder_trad = solution_folder_trad_base + str(dataset_kind_) + "/"
					if not os.path.exists(solution_folder_trad): os.makedirs(solution_folder_trad)
					f_out_trad = open(solution_folder_trad + "solutions_trad_Sums" + str(n_folder_app) + ".csv", "w")

				if TSbC_flag or TSaC_flag:
					trust_file_adapt_for_iter = os.path.join(trust_file_base, "trad_trust_est_at_eac_iter" + str(dir_name) + ".csv")
					trust_file_adapt = os.path.join(trust_file_base, "trad_trust_est" + str(dir_name) + ".csv")

				if TSbC_flag:
					solution_folder_adapt = solution_folder_adapt_base + str(dataset_kind_) + "/"
					if not os.path.exists(solution_folder_adapt): os.makedirs(solution_folder_adapt)
					f_out_TSbC = open(solution_folder_adapt + "solutions_best_children" + str(n_folder_app) + ".csv", "w")

				if TSaC_flag:
					solution_folder_adapt = solution_folder_adapt_base + str(dataset_kind_) + "/"
					if not os.path.exists(solution_folder_adapt): os.makedirs(solution_folder_adapt)
					f_out_TSaC = open(solution_folder_adapt + "solutions_all_children" + str(n_folder_app) + ".csv", "w")

				# clear all the variable to not overload the memory
				dataitem_ids.clear()
				D.clear()
				T.clear()
				S_set.clear()
				S.clear()
				F_s.clear()
				S_prop.clear()
				sources_dataItemValues.clear()
				dataitem_values_info.clear()
				fact_and_source_info.clear()

				if TSbC_flag == True or TSaC_flag == True:
					res_list = preprocessing_sums_model.preprocess_before_running_model(source_file, facts_file,
															   confidence_value_computation_info_dir, dataitem_index_file,
															   g)
					T = res_list[0]
					T_actual = res_list[1]
					sources_dataItemValues = res_list[2]
					D = res_list[3]
					F_s = res_list[4]
					S = res_list[5]
					S_prop = res_list[6]
					app_conf_dict = res_list[7]
					# [T, sources_dataItemValues_, D_, F_s_, S_, S_prop_, app_conf_dict_]
				else:
					res_list = preprocessing_sums_model.preprocess_before_running_model_only_trad(source_file, facts_file)
					T = res_list[0]
					sources_dataItemValues = res_list[1]
					F_s = res_list[2]
					S = res_list[3]
				#######################################################################################################
				################all the informaiton required are uploaded, NOW the experiments start###################
				#######################################################################################################
				if Sums_flag:
					print("Sums Experiments")

					res_t = sums_model.run_sums_saving_iter(copy.deepcopy(T), F_s, S, initial_confidence, max_iteration_number, trust_file_trad_for_iter)
					if res_t:
						trust_trad = res_t[0]
						conf_trad = res_t[1]
						''' WRITE estimations RESULTS --> if you want do that de-comment both following lines'''
						res = utils_writing_results.writing_trust_results(trust_file_trad, trust_trad)
						if not res:
							print("error in writing trust estimation file for traditional model")
							exit()
						#res = utils_writing_results.writing_confidence_results_trad(conf_file_trad, conf_trad)
						if not res:
							print("error in writing conf estimation file for traditional model")
							exit()
						##############################################################################################################
						print("Starting selection of true values algorithm for trad sums.....")
						dict_solution_TRAD = selection_algorithm.compute_trad_performance_final(predicate_info, conf_trad,
																				 sources_dataItemValues, k_expected)

						missing_dataitems = 0
						for dataitem in ground:
							if dataitem not in dict_solution_TRAD:
								missing_dataitems += 1
							else:
								list_app = dict_solution_TRAD[dataitem]
								out_str = ""
								for item in list_app:
									out_str += str(item) + " "
								out_str = out_str[:-1]

								if predicate == "genre":
									dataitem = bytes(dataitem, 'unicode-escape')
									dataitem = str(dataitem, 'utf-8')
									f_out_trad.write(str(dataitem) + '\t' + str(out_str) + '\n')
								else:
									f_out_trad.write(str(dataitem) + '\t' + str(out_str) + '\n')
							f_out_trad.flush()
						f_out_trad.close()

					else:
						print("Error in traditional model")

				#######################################################################################################
				print("Adapted Sums Experiments")
				res_a = sums_model.run_adapted_sums_saving_iter(copy.deepcopy(T), F_s, S_prop, initial_confidence,
														   max_iteration_number, sources_dataItemValues, trust_file_adapt_for_iter)
				if res_a:
					trust_adapt = res_a[0]
					conf_adapt = res_a[1]
					''' WRITE estimations RESULTS --> if you want do that de-comment both following lines'''
					res = utils_writing_results.writing_trust_results(trust_file_adapt, trust_adapt)
					if not res:
						print("error in writing trust estimation file for traditional model")
						exit()
					trust_average = utils_dataset.compute_average_trustworhiness(S_prop, trust_adapt)  # T_average is a dict with key = claim_id and
					descendants = predicate_info[1]
					ancestors = predicate_info[2]
					T_average_normalized = utils_dataset.normalize_trust_average(trust_average, ancestors, descendants,
																   sources_dataItemValues)
					#res = utils_writing_results.writing_confidence_results_adapted(conf_file_adapt, conf_adapt, trust_average,T_average_normalized)
					if not res:
						print("error in writing conf estimation file for traditional model")
						exit()
					##############################################################################################################
					print("computing normalized confidence")
					conf_adapt_norm = utils_normalize_conf.creating_normalized_for_d_estimation_optimized(ground, conf_adapt, app_conf_dict)
					for item in conf_adapt_norm:
						if item.startswith("P01744_1"):
							print(str(item) + "\t" + str(conf_adapt_norm[item]))

					gc.collect()
					if TSbC_flag:
						print("Starting selection of true values algorithm for adapt model and NORMALIZED trust average.....")
						print("TESTING MODEL -- BestChildren -- delta = 0")
						first_ranking_criteria = "ic"
						second_ranking_criteria = "source_average"
						solutions_dict = selection_algorithm.compute_solution_best_children_final(predicate_info, conf_adapt, conf_adapt_norm,
																						T_average_normalized, k_expected, first_ranking_criteria, second_ranking_criteria, threshold_list)

						dict_solution_IC_final = solutions_dict[0]
						dict_solution_TRUST_final = solutions_dict[1]
						#[dict_solution_IC, dict_solution_TRUST]

						missing_dataitems_IC = 0
						missing_dataitems_TRUST = 0
						for dataitem in ground:
							for threshold in threshold_list:
								if dataitem not in dict_solution_IC_final[threshold] and dataitem not in dict_solution_TRUST_final[threshold]:
									missing_dataitems_IC += 1
								else:
									list_app_IC = dict_solution_IC_final[threshold][dataitem]
									out_IC = ""
									for item in list_app_IC:
										out_IC += str(item) + " "
									out_IC = out_IC[:-1]
									list_app_TRUST = dict_solution_TRUST_final[threshold][dataitem]
									out_TRUST = ""
									for item in list_app_TRUST:
										out_TRUST += str(item) + " "
									out_TRUST = out_TRUST[:-1]
									if predicate == "genre":
										dataitem_to_out = bytes(dataitem, 'unicode-escape')
										dataitem_to_out = str(dataitem_to_out, 'utf-8')
										f_out_TSbC.write(str(threshold) + '\t' + str(dataitem_to_out) + '\t' + str(out_IC)+ '\t' + str(out_TRUST) + '\n')
									else:
										f_out_TSbC.write(str(threshold) + '\t' + str(dataitem) + '\t' + str(out_IC) + '\t' + str(out_TRUST) + '\n')
							f_out_TSbC.flush()
						f_out_TSbC.close()
						##############################################################################################################

					#############################################################################################################

					#continue
					if TSaC_flag:
						print("Starting selection of true values algorithm for adapt model and NORMALIZED trust average.....")
						print("TESTING MODEL -- AllChildren -- delta = 1")
						first_ranking_criteria = "ic"
						second_ranking_criteria = "source_average"
						sources_dataItemValues.clear()
						solutions_dict = selection_algorithm.compute_solution_all_children_final(predicate_info,
																										   conf_adapt,
																										   conf_adapt_norm,
																										   T_average_normalized,
																										   5,
																										   first_ranking_criteria,
																										   second_ranking_criteria, app_conf_dict, threshold_list)
						dict_solution_IC_final = solutions_dict[0]
						dict_solution_TRUST_final = solutions_dict[1]
						# [dict_solution_IC, dict_solution_TRUST]
						#threshold_list = [0, 0.1, 0.2, 0.3, 0.4, 0.5]#[0, 0.1, 0.2, 0.3, 0.4, 0.5]
						missing_dataitems_IC = 0
						missing_dataitems_TRUST = 0
						for dataitem in ground:
							for threshold in threshold_list:
								if dataitem not in dict_solution_IC_final[threshold] and dataitem not in dict_solution_TRUST_final[threshold]:
									missing_dataitems_IC += 1
								else:
									list_app_IC = dict_solution_IC_final[threshold][dataitem]
									out_IC = ""
									for item in list_app_IC:
										out_IC += str(item) + " "
									out_IC = out_IC[:-1]
									list_app_TRUST = dict_solution_TRUST_final[threshold][dataitem]
									out_TRUST = ""
									for item in list_app_TRUST:
										out_TRUST += str(item) + " "
									out_TRUST = out_TRUST[:-1]
									if predicate == "genre":
										dataitem_to_out = bytes(dataitem, 'unicode-escape')
										dataitem_to_out = str(dataitem_to_out, 'utf-8')
										f_out_TSaC.write(str(threshold) + '\t' + str(dataitem_to_out) + '\t' + str(
											out_IC) + '\t' + str(out_TRUST) + '\n')
										#f_out.write(str(threshold) + '\t' + str(dataitem.encode("utf-8")) + '\t' + str(out_IC) + '\t' + str(out_TRUST) + '\n')
									else:
										f_out_TSaC.write(str(threshold) + '\t' + str(dataitem) + '\t' + str(out_IC) + '\t' + str(
											out_TRUST) + '\n')
							f_out_TSaC.flush()
						f_out_TSaC.close()
					cont_datasets += 1
					#elimina folder with info for belief propagation
					shutil.rmtree(confidence_value_computation_info_dir)
					os.remove(dataitem_index_file)
					print("process dataset " + str(cont_datasets) + "/20")
				#######################################################################################################
				else:
					print("Error in adapted model")


			# only the first level of subfolder
			cont_subfolders += 1
			# logging.info("subfolder numero " + str(cont_subfolders))
			# logging.info("cont datasets " + str(cont))
			if cont_subfolders == 3:
				break

	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise
		exit()
