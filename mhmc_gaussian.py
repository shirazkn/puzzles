"""
Use a Metropolis-Hastings Markov Chain to estimate (unknown) mean of Gaussian data
Compare MH samples to known conditional pdf of mean given data and prior
"""

import scipy as sp
import numpy as np
import matplotlib.pyplot as plt


def ones_vector():
    return np.ones([20, 1])


def generate_iid_normal(_mean, _cov, samples):
    _data = []
    for i in range(samples):
        _data.append(sp.random.normal(_mean, _cov))
    return np.array(_data)


def pdf_mean_given_data(x, _data):
    sample_mean = np.average(_data)
    _mean = sample_mean*20/21
    _var = 1/21
    return (1/np.sqrt(2*np.pi*_var)) * (np.exp(-(0.5/_var)*(x - _mean)**2))


def pdf_data_given_mean(x, _mean):
    _var = 1
    exponent = 0.0
    for point in x:
        exponent += (point - _mean)**2
    return (1/np.sqrt(2*np.pi*_var)**20) * np.exp(-(0.5/_var)*exponent)


def pdf_mean(x):
    _var = 1
    return 1/np.sqrt(2*np.pi*_var) * np.exp(-0.5*x**2)


def discrete_gaussian_walk(x):
    return x + sp.random.normal(0, 0.25)


def likelihood_ratio(_data, param_1, param_2):
    return pdf_data_given_mean(_data, param_2)*pdf_mean(param_2)/(pdf_data_given_mean(_data, param_1)*pdf_mean(param_1))


def mc_sample(_data, proposal, length):
    samples = [proposal]
    for i in range(length):
        sample = discrete_gaussian_walk(proposal)
        if sp.random.uniform(0, 1) < likelihood_ratio(_data, proposal, sample):
            samples.append(sample)
            proposal = sample
        else:
            samples.append(proposal)

    return samples


if __name__ == "__main__":
    true_mean = sp.random.normal(0, 1)
    data = generate_iid_normal(_mean=true_mean, _cov=1, samples=20)
    mc_samples = mc_sample(data, 0.0, 20000)
    true_density = []
    xs = np.linspace(np.min(mc_samples), np.max(mc_samples), 1000)
    for x in xs:
        true_density.append(pdf_mean_given_data(x, data))

    _ = plt.hist(x=np.array(mc_samples), bins=40, density=True, label="Metropolis-Hastings Samples")
    plt.plot(xs, true_density, 'black', label="True Distribution")
    plt.legend()
    plt.show()

