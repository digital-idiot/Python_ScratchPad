import math
import random
import re


def is_valid_index_type(index):
    if type(index) is int:
        return True
    else:
        return False


def is_valid_data_type(rna):
    if type(rna) is str:
        return True
    else:
        return False


def is_valid_length(rna):
    if is_valid_data_type(rna):
        if len(rna) % 3 == 0:
            return True
        else:
            return False
    else:
        return None


def is_valid_data(rna):
    if is_valid_data_type(rna):
        uni_set = {'A', 'G', 'C', 'U'}
        input_set = set(rna)
        if input_set.issubset(uni_set):
            return True
        else:
            return False
    else:
        return None


def get_codon_list(rna):
    if is_valid_data_type(rna):
        codon_size = 3
        return [rna[i:i + codon_size] for i in range(0, len(rna), codon_size)]
    else:
        return None


def get_nth_codon(rna, index):
    if is_valid_data_type(rna) and is_valid_index_type(index) and (index < math.ceil(len(rna)/3)):
        codon_list = get_codon_list(rna)
        return codon_list[index - 1]
    else:
        return None


amino_acid_to_codon = dict()
amino_acid_to_codon['Alanine'.upper()] = {'GCU', 'GCC', 'GCA', 'GCG'}
amino_acid_to_codon['Arginine'.upper()] = {'CGU', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'}
amino_acid_to_codon['Asparagine'.upper()] = {'AAU', 'AAC'}
amino_acid_to_codon['Aspartic acid'.upper()] = {'GAU', 'GAC'}
amino_acid_to_codon['Cysteine'.upper()] = {'UGU', 'UGC'}
amino_acid_to_codon['Glutamine'.upper()] = {'CAA', 'CAG'}
amino_acid_to_codon['Glutamic acid'.upper()] = {'GAA', 'GAG'}
amino_acid_to_codon['Glycine'.upper()] = {'GGU', 'GGC', 'GGA', 'GGG'}
amino_acid_to_codon['Histidine'.upper()] = {'CAU', 'CAC'}
amino_acid_to_codon['Isoleucine'.upper()] = {'AUU', 'AUC', 'AUA'}
amino_acid_to_codon['Start'.upper()] = {'AUG'}
amino_acid_to_codon['Leucine'.upper()] = {'UUA', 'UUG', 'CUU', 'CUC', 'CUA', 'CUG'}
amino_acid_to_codon['Lysine'.upper()] = {'AAA', 'AAG'}
amino_acid_to_codon['Phenylalanine'.upper()] = {'UUU', 'UUC'}
amino_acid_to_codon['Proline'.upper()] = {'CCU', 'CCC', 'CCA', 'CCG'}
amino_acid_to_codon['Serine'.upper()] = {'UCU', 'UCC', 'UCA', 'UCG', 'AGU', 'AGC'}
amino_acid_to_codon['Threonine'.upper()] = {'ACU', 'ACC', 'ACA', 'ACG'}
amino_acid_to_codon['Tryptophan'.upper()] = {'UGG'}
amino_acid_to_codon['Tyrosine'.upper()] = {'UAU', 'UAC'}
amino_acid_to_codon['Valine'.upper()] = {' 	GUU', 'GUC', 'GUA', 'GUG'}
amino_acid_to_codon['Stop'.upper()] = {'UAA', 'UGA', 'UAG'}

codon_map = {'AUG': 'METHIONINE', 'UAA': 'OCHRE', 'UGA': 'OPAL', 'UAG': 'AMBER'}


def random_sequence(n, flag=True):
    if type(flag) is bool:
        if type(n) in [int, float]:
            if flag:
                if type(n) is float:
                    n = int(round(n))
                if n % 3 != 0:
                    print("Warning: Sequence Length is not a Multiple of 3")
                    print("Note: Using Nearest Number divisible by 3")
                    n = 3 * round(n / 3)
            rna_nucleotides = ('A', 'C', 'G', 'U')
            result = str()
            while n > 0:
                result = result + random.choice(rna_nucleotides)
                n = n - 1
            return result
        else:
            print("Invalid Argument Type")
            return None
    else:
        print("Invalid Argument Type")
        return None


def get_slice(rna_string, index):
    if is_valid_data_type(rna_string) and is_valid_data_type(index):
        regex = r"(AUG[AUGC]*?(UAA|UGA|UAG))"
        return re.search(regex, rna_string[index:], re.I)


def get_all_slice(rna_string):
    if is_valid_data_type(rna_string):
        regex = r"(AUG[AUGC]*?(UAA|UGA|UAG))"
        slice_list = list()
        for match in re.finditer(regex, rna_string, re.I):
            index_pair = (match.start(0), match.end(0))
            match_info = (match.group(0), index_pair)
            slice_list.append(match_info)
        return slice_list
    else:
        return None


def get_all_valid_slice(rna_string):
    if is_valid_data_type(rna_string):
        slice_info = get_all_slice(rna_string)
        valid_slice_list = list()
        if slice_info is not None:
            for current_slice_info in slice_info:
                if len(current_slice_info[0]) % 3 == 0:
                    valid_slice_list.append(current_slice_info)
            return valid_slice_list
        else:
            return None
    else:
        return None


def is_valid_sequence(sequence):
    if is_valid_data_type(sequence) and is_valid_length(sequence):  # and is_valid_data(sequence):
        regex = r'(^AUG[AUGC]*?(UAA|UGA|UAG)$)'
        sample = re.search(regex, sequence, re.I).group(1)
        if sequence == sample:
            return True
        else:
            return False
    else:
        return None


def translate_into_amino_acids(sequence):
    if is_valid_sequence(sequence):
        codon_list = get_codon_list(sequence)
        amino_acid_list = list()
        if codon_list is not None:
            for codon in codon_list:
                for amino_acid in amino_acid_to_codon.keys():
                    if codon in amino_acid_to_codon[amino_acid]:
                        acid_identifier = amino_acid
                        if (amino_acid in {'START', 'STOP'}) and (codon in codon_map.keys()):
                            acid_identifier = amino_acid + " (" + codon_map[codon] + ")"
                        amino_acid_list.append(acid_identifier)
            return amino_acid_list
        else:
            return None
    else:
        return None


rna_str = random_sequence(999999)
slice_lst = get_all_valid_slice(rna_str)
for k in range(len(slice_lst)):
    start = slice_lst[k][1][0]
    stop = slice_lst[k][1][1]
    if slice_lst[k][0] == rna_str[start:stop]:
        print(slice_lst[k][0], "\t", translate_into_amino_acids(slice_lst[k][0]))
