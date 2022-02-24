from Gaussian import Gaussian
from EM import EM
from LNN import LNN
from QNN import QNN

import os
import time
import numpy as np
import scipy.stats as st

sample_number = 500
EM_train_number = 1000
run_number = 20
NN_train_number = 4000

LNN_activation_func_1 = { 0: LNN.softmax }
LNN_activation_func_2 = { 0: LNN.relu, 1: LNN.softmax }
LNN_activation_func_3 = { 0: LNN.relu, 1: LNN.relu, 2: LNN.softmax }
QNN_activation_func_1 = { 0: QNN.softmax }

optimizer_para = {
    "lr":         0.01,     # float, for all optimizer
    "decay_rate": 0.99,     # float, for optimizer "RMSprop"
    "beta1":      0.9,      # float, for optimizer "Adam"
    "beta2":      0.999,    # float, for optimizer "Adam"
    "iter":       0
}

for D in (2, ):
    for K in (6, ):
        result = np.zeros([sample_number, 8])
        for S in range(sample_number):
            set = time.time()
            print(D, K, S)

            LNN_neuron_num_1     = {0: K}
            LNN_neuron_num_2_10  = {0: 10,  1: K}
            LNN_neuron_num_2_50  = {0: 50,  1: K}
            LNN_neuron_num_2_100 = {0: 100, 1: K}
            LNN_neuron_num_3_100 = {0: 100, 1: 50, 2: K}
            QNN_neuron_num_1     = {0: K}

            while True:
                """ Set N_k, mu, and cov """
                N_k = [np.random.randint(3000, 6000) for k in range(K)]
                mu_set = np.array([(np.random.random(D) - 0.5) * 15 for i in range(K)])
                cov_set = []
                for i in range(K):
                    a = np.random.random((D, D)) * 2 - 1
                    cov = np.dot(a, a.T) + np.dot(a, a.T)
                    cov_set.append(cov)

                """ Generate Sample """
                gaussian = Gaussian(mu_set, cov_set)
                train_point, train_label, test_point, test_label, \
                sample_point, sample_label, = \
                    gaussian.generate_sample(N_k)

                """ Bayes inference """
                prio_p = np.divide(N_k, sum(N_k))
                post_p = np.zeros((len(test_point), K))  # [ N * K ]
                for k in range(K):
                    post_p[:, k] = prio_p[k] * \
                                   st.multivariate_normal.pdf(test_point,
                                                              mu_set[k],
                                                              cov_set[k],
                                                              allow_singular=True)
                t = np.argmax(test_label, axis=1)
                y = np.argmax(post_p, axis=1)
                bayes_accuracy = np.sum(y == t) / len(test_point)

                """ EM algorithm """
                em = EM(K)
                em.train(train_point, train_label, EM_train_number)
                em_accuracy = em.test(test_point, test_label)
                if bayes_accuracy - em_accuracy < 0.10: break

            print("em")
            result[S][0] = bayes_accuracy
            result[S][1] = em_accuracy

            qnn = QNN(D, QNN_neuron_num_1, QNN_activation_func_1)
            qnn.train(train_point, train_label, test_point, test_label,
                      NN_train_number, optimizer_para)
            result[S][2] = qnn.accuracy(test_point, test_label)

            lnn = LNN(D, LNN_neuron_num_1, LNN_activation_func_1)
            lnn.train(train_point, train_label, test_point, test_label,
                      NN_train_number, optimizer_para)
            result[S][3] = lnn.accuracy(test_point, test_label)

            lnn = LNN(D, LNN_neuron_num_2_10, LNN_activation_func_2)
            lnn.train(train_point, train_label, test_point, test_label,
                      NN_train_number, optimizer_para)
            result[S][4] = lnn.accuracy(test_point, test_label)

            lnn = LNN(D, LNN_neuron_num_2_50, LNN_activation_func_2)
            lnn.train(train_point, train_label, test_point, test_label,
                      NN_train_number, optimizer_para)
            result[S][5] = lnn.accuracy(test_point, test_label)

            lnn = LNN(D, LNN_neuron_num_2_100, LNN_activation_func_2)
            lnn.train(train_point, train_label, test_point, test_label,
                      NN_train_number, optimizer_para)
            result[S][6] = lnn.accuracy(test_point, test_label)

            lnn = LNN(D, LNN_neuron_num_3_100, LNN_activation_func_3)
            lnn.train(train_point, train_label, test_point, test_label,
                      NN_train_number, optimizer_para)
            result[S][7] = lnn.accuracy(test_point, test_label)

            if not os.path.exists('complex'): os.mkdir('complex')
            np.savetxt("complex/D={}, K={}.csv".format(D, K), result, delimiter=",")

            end = time.time()
            print(end-set)