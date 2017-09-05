#dataset generation
import random
import math
import zipfile
import os
import time
from TDO.dataset_generation import utils_generation
import sys
##Please contact the authors to obtain "value similarity" zip file
##############################################  SOURCE FUNCTIONS    ####################################################
def getSource(new_S, multiplier, lambd):
    #return the index of the source that has to provide a value for a specific data item
    i = int(random.expovariate(lambd)*multiplier)
    while (i >= len(new_S)):
        i = int(random.expovariate(lambd)*multiplier)
    s = new_S[i]
    return int(s.replace('source',''))

def generate_source_number(lambda_nb_sources, multiplier_nb_sources, dim_S):
    #this function returns the number of sources that will provided a value about the dataitem under examination
    sourceNumber = int(random.expovariate(lambda_nb_sources) * multiplier_nb_sources)
    while (sourceNumber < 1 or sourceNumber >= dim_S): #it is possible to obtain sourceNumber = 0
        sourceNumber = int(random.expovariate(lambda_nb_sources) * multiplier_nb_sources)
    return sourceNumber

def source_generation(path_accuracies_file, total_n_sources, mu, sigma):
    #It generates a specific number of sources with the related source trustworthiness level.
    #the trustworthiness level is randomly generated using a normal variate distribution with parameters mu and sigma
    #Save source information (id + source trustworhiness) in a file.
    #return the set of sources and the set of accuracies associate to them.
    #Note that since the source id is a number among 0 and total_n_sources, in A array the accuracy of the source i
    # will be in the position i of the array.
    try:
        S = []  #list of sources
        A = [0] * total_n_sources #list of trustworthiness level of sources, given the source name as index, retrieve the accuracy referred to it
        text_file_acc = open(path_accuracies_file, "w", encoding="utf-8")
        for i in range (0, total_n_sources):
            S.append('source'+str(i))
            a_i = random.normalvariate(mu, sigma) #accuracy of source i
            while (a_i < 0 or a_i> 1):
                a_i = random.normalvariate(mu, sigma)
            A[i] = a_i
            text_file_acc.write('source'+str(i) + '\t' + str(a_i) + '\n' )
        text_file_acc.close()

        return [S, A]
    except:
        print("Error in source generation")
        return None

#########################################  selecting value FUNCTIONS    ################################################
def createBin(bin, ordered_sim_value, sim_dict, threshold_list):
    '''list of values ordered by sim and divided into bin. Each bin contained all the value those sim measure from the solution
    is included in a particular interval. This is done in order to simplify the process.
    The function returns a dict that for each bin return the set of values in it.
    Note that the sim measure (LIN measure) is normalized between 0 and 1
    '''
    pos = 0
    selected_item = ordered_sim_value[pos]
    #start to divide in bin from the more similar value to more different one
    for bin_index in range (0, len(threshold_list)):

        threshold = threshold_list[bin_index]
        bin.append([]) #initialize bin with empty list
        while (sim_dict[selected_item] >= threshold):

            (bin[bin_index]).append(selected_item)
            pos = pos + 1
            if pos < len(ordered_sim_value):
                selected_item = ordered_sim_value[pos]
            else:
                break

    #if I do not fill all the bin, finish the process with empty list
    while bin_index < (len(threshold_list)-1):
        bin.append([])
        bin_index = bin_index + 1
    return bin
    #END BIN CREATION

def getSomeInitialValue(bin, provided_false_values):
    #for each bin, to select a false value
    #Note that is required to avoid situation in which the number of bins is higher than the possible false value
    #so it is possible pick up one value for each bin for initializing the dict
    for bin_index in range (0, len(bin)):
        if len(bin[bin_index]) > 0 : #if in the bin there is at least a value
            value_index = int(random.uniform(0, len(bin[bin_index]))) #from the bin in pos bin_index select a value at value_index position
            value = (bin[int(bin_index)])[value_index]
            provided_false_values.append(value)

    return provided_false_values

def getTrueValue_uniform(true_value_set, multiplier):
    #to pick the true value using a uniform distribution
    value_index = random.randint(0, len(true_value_set)-1)
    #in this way every index is ok. it works when true value set len is < 100 or multiplier
    value = true_value_set[value_index]
    #do not remove the value selected, it could be choosen again
    return value

def getTrueValue_exponential(true_value_set, multiplier):
    # to pick the true value using a exponential distribution
    #Attention!! processing in this way the exponential, it tends to be a uniform curve ---_> we named it LOW_E distribution
    rndm_nb = int(random.expovariate(0.2) * multiplier)
    value_index = int (((rndm_nb * len(true_value_set))) / multiplier)
    #in this way every index is ok. it works when true value set len is < 100 or multiplier
    while value_index < 0 or value_index >= len(true_value_set):
        rndm_nb = int(random.expovariate(0.2) * multiplier)
        value_index = int (((rndm_nb * len(true_value_set))) / multiplier)

    value = true_value_set[value_index]
    #do not remove it, it could be choosen again
    return value

def getTrueValue_beta(true_value_set, multiplier):
    # to pick the true value using a beta distribution
    # Attention!! processing in this way the beta, it tends to be a exponential curve ---_> we named it EXP distribution
    rndm_nb = int(random.betavariate(1,2) * multiplier)
    value_index = int (((rndm_nb * len(true_value_set))) / multiplier)
    #in this way every index is ok. it works when true value set len is < 100 or multiplier
    while value_index < 0 or value_index >= len(true_value_set):
        rndm_nb = int(random.betavariate(1,2) * multiplier)
        value_index = int (((rndm_nb * len(true_value_set))) / multiplier)

    value = true_value_set[value_index]
    #do not remove it, it could be choosen again
    return value

def getFalseValue(provided_false_values, bin, lambda_bin_index):
    '''to pick a false value among the set
    The probability to select a false value, already provided, is higher than selecting a new one.
    provided_false_values is used for this reason
    '''
    value = 'null'
    if (len(set(provided_false_values)) < max_false_domain_cardinality) and (random.random() < 0.4): #selection not in VALUES ALREADY PROVIDED
        bin_index = int(random.expovariate(lambda_bin_index))
        while bin_index < 0 or bin_index >= len(bin):
            bin_index = int(random.expovariate(lambda_bin_index))
        if len(bin[bin_index])==0:
            return None
        if (len(bin[bin_index]) == 1):
            value_index = 0
        else:
            value_index = int(random.randint(0, len(bin[bin_index])-1))#Return a random integer N such that a <= N <= b.
        value = (bin[bin_index])[value_index]
    else: #selection among values already provided
        if (len(provided_false_values) > 0):
            if (len(provided_false_values) == 1):
                value_index = 0
            else:
                value_index = random.randint(0, len(provided_false_values)-1)

            value = provided_false_values[value_index]

    provided_false_values.append(value)
    return [value, provided_false_values]

########################################## CLaims GENERATION FUNCTIONS    ################################################
def fact_generation(path_facts_file, path_values_sim_file, myzipfile, value_sim_ids, truth, D, S, A, ancestors, descendents, descendent, tax_domain, threshold_list, true_distr):
    '''N.B. in order to not reload each time the similarity measures referred to a particular value with all the others -it is an expensive operation-
     We ordered the true facts according to their true values (their solution)
    '''
    sim_dict = dict()
    false_values_bin = []
    provided_false_values = []

    #choice of parameter is based on empirical experiments - to obtain new dataset with other caracheristic, these parameters can be modifiied
    multiplier_sources =  10**(int(math.log10(len(S)-1)) + 1)
    lambda_sources = 4
    lambda_nb_sources = 0.2
    multiplier_nb_sources = 100
    multiplier_true_values = 1
    lambda_bin_index = 0.7

    #initialization of outputfile
    facts_file = open(path_facts_file, 'w', encoding="utf-8")
    facts_file.write("factID\tdataitem\tvalue\tsourceID\n")

    prec_solution = ''
    cont_d = 0
    fact_count = 0
    start = time.time()

    for d in D: #for each dataitem

        solution = truth.get(d) #get the solution(true value) for this dataitem
        if prec_solution != solution: #for each new solution, we need to retrieve the similarity measure with all the other values in the tax
            prec_solution  = str(solution)
            value_id = value_sim_ids[solution]
            #load similarity measure between solution and all the others value (if they are not already loaded)
            sim_dict.clear()
            sim_dict = utils_generation.load_values_sim_measure(path_values_sim_file, myzipfile, value_id, sim_dict)
            #creation of the possible true value set where we can pick the values
            true_value_set = set(ancestors.get(solution))

            #convert the set in list
            true_value_list = list(true_value_set)

            if len(true_value_list) < 2:
                n_digit = 1
            else:
                n_digit=int(math.log10(len(true_value_list)-1) ) + 1
            multiplier_true_values = 10**(n_digit)

            # (i)collect the similarity measure of the value in the possible true value set
            # (ii)delete their similarity measure from the sim measure of false value domain
            sim_dict_true = dict()

            for item in true_value_set:
                if item in sim_dict:
                    sim_dict_true[item] = sim_dict[item]
                    del sim_dict[item]

            if not descendent: #descendants of a solution will not be considered as possible true values
                #deleting the descendent of the solution from the possible false values
                for item in descendents[solution]:
                    if item in sim_dict:
                        del sim_dict[item]

            true_value_list = sorted(sim_dict_true, key = sim_dict_true.__getitem__, reverse = True)

            #order list of false values base on their similarity with the real solution
            ordered_sim_list = sorted(sim_dict, key = sim_dict.__getitem__, reverse = True)
            #divide all the possible values in bin where they can be pick
            false_values_bin.clear()
            false_values_bin = createBin(false_values_bin, ordered_sim_list, sim_dict, threshold_list)

            false_values_bin_copy = false_values_bin.copy()
            true_value_list_copy = true_value_list.copy()
        else:#reinitialization, if the solution is the same of the previous data item - it saves time
            false_values_bin = false_values_bin_copy.copy()
            true_value_list = true_value_list_copy.copy()


        #after the initialization of all the set
        provided_false_values.clear()
        provided_false_values = getSomeInitialValue(false_values_bin, provided_false_values)

        #generate the number of sources that provided a fact for this dataitem
        sourceNumber = generate_source_number(lambda_nb_sources, multiplier_nb_sources, len(S))

        new_S = S.copy()  #ccopy this list, list otherwise I do not have fix position in the set and I cannot applyP

        for b in range(0, sourceNumber):
            s = getSource(new_S, multiplier_sources, lambda_sources) #pick up a source
            new_S.remove('source' + str(s))  #remove S ... One source cannot provided two value for the same dataitem

            if random.random() < A[s]: #according to its accuracy a source provide a true or false value
                if true_distr == "uniform": value = getTrueValue_uniform(true_value_list, multiplier_true_values)
                if true_distr == "exponential": value = getTrueValue_exponential(true_value_list, multiplier_true_values)
                if true_distr == "beta": value = getTrueValue_beta(true_value_list, multiplier_true_values)
            else:
                false_value_infos = getFalseValue(provided_false_values, false_values_bin, lambda_bin_index)
                if false_value_infos == None: continue
                value =  false_value_infos[0]
                provided_false_values = false_value_infos[1]

            facts_file.write(str(fact_count) + '\t' + str(d) + '\t' + str(value) + '\t' + str(s) + '\n')
            fact_count = fact_count + 1

        #end facts for specific dataitem

        cont_d = cont_d + 1
        if (cont_d%50 == 0):
            print('processed dataitems : ' + str(cont_d) + '/' + str(len(D)))
            print ("numb of generated facts : " + str(fact_count))
            act_time = time.time() - start
            print ("Running time until now in sec: " + str(act_time) + ".....")
            facts_file.flush()

    facts_file.close()
    return  fact_count
   #end FACT GENERATION

if __name__ == "__main__":
    #Please contact the authors to obtain "value similarity" zip file
    #n_min - n_max intervalc ontains the id_datasets that will be generated
    try:
        predicate = str(sys.argv[1])
        n_min = int(sys.argv[2])
        n_max = int(sys.argv[3])
        true_distr = str(sys.argv[4])
        total_n_sources = int(sys.argv[5])
        if not ((predicate == 'genre') or (predicate == 'birthPlace')):
            print("errors in the parameters")
            exit()
        if not ((true_distr == 'exponential') or (true_distr == 'uniform')or (true_distr == 'beta')):
            print("errors in the parameters")
            exit()
    except:
        print("errors in the parameters")
        exit()

    max_false_domain_cardinality = 30
    threshold_list = [0.80, 0.60, 0.40, 0.00]
    mu_sources = 0.6
    sigma_sources = 0.4

    # Inputs
    cwd_here = os.getcwd()
    base_directory = cwd_here.replace("\\dataset_generation", "")

    base_dir = base_directory + "\\required_files\\"
    if predicate == 'genre':
        base_dir = base_dir + "genre\\"
        path_ancestor_file =  base_dir + 'ancestors_heuristic_genre_base.csv'
        path_descendent_file = base_dir + 'descendants_genre_base.csv'
        path_ground_file = base_dir + 'sample_genre_base_3.csv'

        path_values_sim_ids_file = base_dir + 'sample_genre_base_3_values.csv'
        path_sim_measures = 'similarities\\similarities_3.zip'
        path_values_sim_file = 'similarities_3/sim_'
    else:#the predicate is 'birthPlace'
        base_dir = base_dir + "birthPlace\\"
        path_ancestor_file = base_dir + 'ancestors_heuristic.csv'
        path_descendent_file = base_dir + 'specific_value.csv'
        path_ground_file = base_dir + 'sample_ground_grouped.csv'

        path_values_sim_ids_file = base_dir + 'sample_ground_values.csv'
        path_sim_measures = 'similarities\\similarities.zip'
        path_values_sim_file = 'similarities/sim_'
    #load descendants
    descendent = False
    if not descendent:
        descendents = utils_generation.loading_descendents(path_descendent_file)
        print ('number of values in value_descendents ' + str(len(descendents)))
    #laod ancestors
    tax_infos = utils_generation.loading_ancestors(path_ancestor_file) #return a list tax_infos[0] = dict <key = value, value = list of ancestors>, tax_infos[1] = set with all the values in taxonomy
    if tax_infos == None: exit()
    ancestors = tax_infos[0]
    tax_domain = tax_infos[1]
    print ('number of values in value_ancestor ' + str(len(ancestors)))
    print ('number of values in the taxonomy ' + str(len(tax_domain)))
    #load ground truth
    truth_infos = utils_generation.loading_ground_truth(path_ground_file)
    if truth_infos == None: exit()
    truth = truth_infos[0]
    #do not use set otherwise you lost the order grouped by solution
    D = truth_infos[1] #actually since is the ground truth we have repetition in data item
    print ('number of dataitems ' + str(len(D)))

    #loading of value ids for value similarity
    value_sim_ids = utils_generation.loading_values_sim_ids(path_values_sim_ids_file)
    myzipfile = zipfile.ZipFile(path_sim_measures)

    #the procedure for generating the datasets starts
    for n_of_dataset in range (n_min, n_max):
        print ('DATASET NUMBER ' + str(n_of_dataset) + '.............. with distribution ' + str(true_distr))

        #input file --> as to be update each time that we generate a new dataset with the new dataset id
        basic_path_dataset = 'dataset/dataset_' + str(n_of_dataset) + '/'
        '''two output file: (i) it contains the set of facts - each row contains factID+dataItem+value+source
                           (ii) it contains the set of sources - each row contains sourceID+trustworthiness level'''
        path_facts_file = basic_path_dataset + 'facts_' + str(n_of_dataset) + '.csv'
        path_accuracies_file = basic_path_dataset + "Output_acc_" + str(n_of_dataset) + ".txt"
        if not os.path.exists(basic_path_dataset): os.makedirs(basic_path_dataset)

        #generation of n_sources sources
        source_infos = source_generation(path_accuracies_file, total_n_sources, mu_sources, sigma_sources)
        if source_infos == None: exit()
        S = source_infos[0] #both are list
        A = source_infos[1]
        print ('Number of generated sources ' + str(len(S)))

        #generation of facts - it is the core function
        print ('generation of facts....')
        nb_facts = fact_generation(path_facts_file, path_values_sim_file, myzipfile, value_sim_ids, truth, D, S, A, ancestors, descendents, descendent, tax_domain, threshold_list, true_distr)
        print ('Number of generated facts ' + str(nb_facts))

        print ("End creation of " + str(n_of_dataset) + " dataset")
        print ('-----------------------------------------------------------------')


    myzipfile.close()
    print ("End dataset generation ")