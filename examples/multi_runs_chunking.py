import os
import itertools
import sys
homedir = os.path.expanduser('~')

gpus_idx = list(map(int, sys.argv[1].split()))
gpu_idx = int(sys.argv[2])

group_idx = gpus_idx.index(gpu_idx)
num_groups = len(gpus_idx)

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

hidden_sizes = [500] # 500 is little better than 300
tag_spaces = [140] # 80 is bad, 160 is bad for hidden size of 300, 128 and 160 are hard to decide for hidden size of 500
gammas = [0]
learning_rates = [0.01] # 0.02 is bad
decay_rates = [0.01] # should be less than 0.05, 0.01 should be better than 0.03
char_dims = [30]
char_hidden_sizes = [30]
max_norms = [10] # 5 is bad, 10 should be better than 20

num_repeat = 3

dropouts = ['weight_drop'] # this setting yields two results: 95.07, 95.00, 95.04, 95.03
p_ems = [.3] # 0.3 should be better than 0.2
p_ins = [.25]
p_rnns = [(0.2, 0.02)] # 0.2 is better than 0.1
p_outs = [.3] # 0.3 should be better than 0.2


# hidden_sizes = [500] # 500 is little better than 300
# tag_spaces = [140] # 80 is bad, 160 is bad for hidden size of 300, 128 and 160 are hard to decide for hidden size of 500
# gammas = [0]
# learning_rates = [0.01] # 0.02 is bad
# decay_rates = [0.01] # should be less than 0.05, 0.01 should be better than 0.03
# char_dims = [30]
# char_hidden_sizes = [30]
# max_norms = [10] # 5 is bad, 10 should be better than 20
# dropouts = ['std'] # this setting yields results: 95.01, 95.00, 94.99, 94.82
# p_ems = [0.25] # should be less than 0.3 and 0.2 is better than 0.1
# p_ins = [.35] # 0.33 and 0.4 hard to make decision 
# p_rnns = [(0.2, 0.4)] # 0.2 is mostly better than 0.33, 0.2 is better than 0.25 and 0.15
# p_outs = [.3] # 0.4 is mostly better than 0.5 and 0.3 is mostly better than 0.4

batch_sizes = [16]
char_methods = ['cnn']

parameters = [hidden_sizes, tag_spaces, gammas, learning_rates, decay_rates, p_ems, p_ins, p_rnns, p_outs, dropouts, char_methods, \
			  batch_sizes, char_dims, char_hidden_sizes, max_norms]
parameters = list(itertools.product(*parameters)) * num_repeat
parameters = list(split(parameters, num_groups))

dataset_name = 'conll00'

params = parameters[group_idx]
for param in params:
	hidden_size, tag_space, gamma, learning_rate, decay_rate, p_em, p_in, p_rnn, p_out, dropout, char_method, batch_size, char_dim, \
																									char_hidden_size, max_norm = param
	result_file_path = 'results/hyperparameters_tuning_{}_{}'.format(dataset_name, gpu_idx)
	p_rnn = '{} {}'.format(p_rnn[0], p_rnn[1])
	log_msg = '\nhidden_size: {}\ttag_space: {}\tgamma: {}\tlearning_rate: {}\tdecay_rate: {}\tp_em: {}\tp_in: {}\tp_rnn: {}\tp_out: {}\ndropout: {}\tchar_method: {}\tbatch_size: {}\
					char_dim: {}\tchar_hidden_size: {}\tmax_norm: {}\n'.format(hidden_size, tag_space, gamma, learning_rate, decay_rate, p_em, p_in, p_rnn, p_out, dropout, char_method, batch_size, char_dim, char_hidden_size, max_norm)
	with open(result_file_path, 'a') as ofile:
		ofile.write(log_msg)
	print(log_msg)
	command = 'CUDA_VISIBLE_DEVICES={} python examples/ChunkingCRF_conll.py --cuda --mode LSTM --encoder_mode lstm --char_method {} --num_epochs 200 --batch_size {} --hidden_size {} --num_layers 1 \
				 --char_dim {} --char_hidden_size {} --tag_space {} --max_norm {} --gpu_id {} --results_folder results --tmp_folder tmp --alphabets_folder data/alphabets \
				 --learning_rate {} --decay_rate {} --schedule 1 --gamma {} --o_tag O --dataset_name {} \
				 --dropout {} --p_em {} --p_in {} --p_rnn {} --p_out {} --unk_replace 0.0 --bigram --result_file_path {}\
				 --embedding glove --embedding_dict "/data/medg/misc/jindi/nlp/embeddings/glove.6B/glove.6B.100d.txt" \
				 --train "/data/medg/misc/jindi/nlp/conll00/train.txt" --dev "/data/medg/misc/jindi/nlp/conll00/dev.txt" \
				 --test "/data/medg/misc/jindi/nlp/conll00/test.txt"'.format(gpu_idx, char_method, batch_size, hidden_size, char_dim, char_hidden_size, tag_space, max_norm, gpu_idx, learning_rate, decay_rate, gamma, dataset_name, dropout, p_em, p_in, p_rnn, p_out, result_file_path)
	os.system(command)

