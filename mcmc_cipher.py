"""
Learn a Markov model of English; use that to infer a cipher
"""
import numpy as np
from copy import deepcopy

ord_A = ord('A')
ord_Z = ord('Z')


def character_from_index(index):
    if 0 <= index < 26:
        return chr(ord_A + index)
    else:
        return ""


def remove_punctuation(text):
    """
    For simplicity we ignore any punctuation besides " "
    """
    unpunctuated_text = ""
    for t in text:
        unpunctuated_text += character_from_index(ord(t.upper()) - ord_A)
        if t == " ":
            unpunctuated_text += t
    return unpunctuated_text


def sanitize_string(raw_string):
    """
    Takes 4 characters at a time and checks whether they're usable (i.e. are letters or space)
    :param raw_string: e.g. "A.FG"
    :return: (boolean, string, <list of indices 0 to 26, where index 27 is a space>)
    NOTE: Some of this is redundant with remove_punctuation()!
    """
    string = ""
    indices = [None, None]
    for i in range(2):
        char, indices[i] = get_character(raw_string[i])
        string += char
    return string, indices


def get_character(char):
    ordinal = ord(char.upper())
    if ord_Z >= ordinal >= ord_A:
        return char.upper(), ordinal - ord_A
    else:
        return " ", 26


class Decryptor:
    def __init__(self, from_cipher: dict = None, with_permutation: [chr, chr] = None):
        if from_cipher is None:
            letter = 'A'
            self.cipher = {}
            for _ in range(26):
                self.cipher[letter] = letter
                letter = chr(ord(letter)+1)
            self.cipher[" "] = " "
        else:
            self.cipher = deepcopy(from_cipher)
            temp = self.cipher[with_permutation[0]]
            self.cipher[with_permutation[0]] = self.cipher[with_permutation[1]]
            self.cipher[with_permutation[1]] = temp

    def decrypt(self, text):
        decrypted_text = ""
        for char in text:
            decrypted_text = decrypted_text + self.cipher[char]
        return decrypted_text

    def encrypt(self):
        raise NotImplementedError("Not needed for this program...")


class EnglishModel:
    def __init__(self, source):
        self.model = np.ones([27, 27])

        for position in range(len(source) - 1):
            raw_string = source[position:position+2]
            _, indices = sanitize_string(raw_string)
            self.model[indices[0], indices[1]] += 1

        for i in range(27):
            normalizer = np.sum(self.model[i, :])
            for j in range(27):
                self.model[i, j] /= normalizer

    def log_pmf_string(self, raw_string):
        string = remove_punctuation(raw_string)
        p = 0.0
        for i in range(len(string) - 1):
            _, indices = sanitize_string(string[i:i+2])
            p += np.log(self.model[indices[0], indices[1]])
        return p


class MCMC:
    def __init__(self, model: EnglishModel):
        self.model = model
        self.state = Decryptor()
        self.proposal = None

    def propose(self):
        random_permutation = (character_from_index(np.random.randint(26)), character_from_index(np.random.randint(26)))
        self.proposal = Decryptor(from_cipher=self.state.cipher, with_permutation=random_permutation)

    def step(self, length, encrypted_text, window=8):
        max_log_pmf = -np.inf
        decrypted_text = None
        for i in range(length):
            random_position = np.random.randint(len(encrypted_text) - window)
            self.propose()
            u = np.random.uniform(0, 1)
            log_pmf_1 = self.model.log_pmf_string(self.proposal.decrypt(encrypted_text[random_position:random_position+window]))
            log_pmf_2 = self.model.log_pmf_string(self.state.decrypt(encrypted_text[random_position:random_position+window]))
            log_likelihood = (log_pmf_1 - log_pmf_2)
            if u < np.exp(log_likelihood):  # Small probability of exploration
                self.state = self.proposal
                if self.model.log_pmf_string(self.proposal.decrypt(encrypted_text)) > max_log_pmf:
                    decrypted_text = self.proposal.decrypt(encrypted_text)
                    max_log_pmf = self.model.log_pmf_string(self.proposal.decrypt(encrypted_text))
        return decrypted_text


if __name__ == "__main__":
    with open("media/texts/norwegian_wood.txt", 'r') as f:
        text_nw = remove_punctuation(f.read())

    model = EnglishModel(text_nw)

    with open("media/texts/encrypted_1.txt", 'r') as f:
        encrypted_text_1 = remove_punctuation(f.read())
    with open("media/texts/encrypted_2.txt", 'r') as f:
        encrypted_text_2 = remove_punctuation(f.read())

    print("Probability of `MMDON' is ", np.exp(model.log_pmf_string("MMdon")))
    print("Probability of `TESTI' is", np.exp(model.log_pmf_string("testi")))
    print("Probability of `TCSTI' is", np.exp(model.log_pmf_string("tcsti")))
    mcmc = MCMC(model)
    print(mcmc.step(100000, encrypted_text_1, window=200))
